import pandas as pd
import numpy as np
import duckdb
import os
from data_io.data_io import execute_query, write_data


def jaccard_containment_similarity(x, y): 
    """
    Calculate the Jaccard-Containment similarity between two sets.

    The Jaccard-Containment similarity is a measure of the overlap between two sets. 
    It is calculated as the size of the intersection divided by the size of the union of the two sets, 
    plus a containment score which is 1 if one set is contained within the other, and 0 otherwise. 
    The final similarity score is the average of the Jaccard similarity and the containment score.

    Parameters:
    x (set): The first set.
    y (set): The second set.

    Returns:
    float: The Jaccard-Containment similarity between x and y.
    """
    intersection_cardinality = len(set.intersection(*[set(x), set(y)]))
    union_cardinality = len(set.union(*[set(x), set(y)]))
    jaccard_similarity = intersection_cardinality / float(union_cardinality)
    
    containment_score = 1 if x in y or y in x else 0
    
    return 0.5 * jaccard_similarity + 0.5 * containment_score


def find_most_similar_rows(main_df, reference_df, column_name, custom_similarity_func):
    """
    Find the most similar rows in a reference DataFrame for each row in the main DataFrame.

    This function computes a similarity matrix between the 'time_and_space_obf' column of the main DataFrame 
    and a specified column of the reference DataFrame using a custom similarity function. 
    It then finds the index of the most similar row in the reference DataFrame for each row in the main DataFrame. 
    The most similar rows are added to the main DataFrame as a new column.

    Parameters:
    main_df (pandas.DataFrame): The main DataFrame.
    reference_df (pandas.DataFrame): The reference DataFrame.
    column_name (str): The name of the column in the reference DataFrame to compute similarities with.
    custom_similarity_func (function): The custom function to compute similarities. 
                                        This function should take two arguments (two sets) and return a similarity score.

    Returns:
    None. The main_df is modified in-place to include a new column with the most similar rows from the reference DataFrame.
    """
    similarity_matrix = np.vectorize(custom_similarity_func)(main_df['time_and_space_obf'].values[:, None], reference_df[column_name].values)
    most_similar_indices = np.argmax(similarity_matrix, axis=1)
    most_similar_rows = reference_df.iloc[most_similar_indices]
    main_df[f'most_similar_{column_name}'] = most_similar_rows[column_name].reset_index(drop=True)


def is_matching_location(row, location_df):
    """
    Check if a row's most similar section, district, and neighborhood match with any location in a DataFrame.

    This function checks if the 'most_similar_section', 'most_similar_district_name', and 
    'most_similar_neighborhood_name' values in a given row match with any location in the location DataFrame. 
    A location is considered a match if the section, district name, and neighborhood name all match.

    Parameters:
    row (pandas.Series): A row from a DataFrame. 
                         This row should contain 'most_similar_section', 'most_similar_district_name', 
                         and 'most_similar_neighborhood_name' columns.
    location_df (pandas.DataFrame): A DataFrame containing location data. 
                                    This DataFrame should contain 'section', 'district_name', 
                                    and 'neighborhood_name' columns.

    Returns:
    bool: True if a matching location is found in location_df, False otherwise.
    """
    section_match = location_df['section'] == row['most_similar_section']

    if not location_df[section_match].empty:
        district_match = location_df['district_name'].iloc[0] == row['most_similar_district_name']
        neighborhood_match = location_df['neighborhood_name'].iloc[0] == row['most_similar_neighborhood_name']
        return district_match and neighborhood_match
    else:
        return False


def mark_discard_flag(row, location_df):
    """
    Mark a row for discard if its most similar section, district, and neighborhood do not match with any location in a DataFrame.

    This function uses the `is_matching_location` function to check if the 'most_similar_section', 
    'most_similar_district_name', and 'most_similar_neighborhood_name' values in a given row match with any location 
    in the location DataFrame. If a matching location is not found, the row is marked for discard.

    Parameters:
    row (pandas.Series): A row from a DataFrame. 
                         This row should contain 'most_similar_section', 'most_similar_district_name', 
                         and 'most_similar_neighborhood_name' columns.
    location_df (pandas.DataFrame): A DataFrame containing location data. 
                                    This DataFrame should contain 'section', 'district_name', 
                                    and 'neighborhood_name' columns.

    Returns:
    bool: True if a matching location is not found in location_df (i.e., the row should be discarded), False otherwise.
    """
    return not is_matching_location(row, location_df)


def add_valid_year_flag(df):
    """
    Add a flag to a DataFrame indicating whether each row's year is valid.

    This function checks if the 'year' value in each row of the given DataFrame is present in the global `year_df` DataFrame. 
    It adds a new column 'valid_year' to the DataFrame, which is True for rows with a valid year and False for rows with an invalid year.

    Parameters:
    df (pandas.DataFrame): A DataFrame containing a 'year' column.

    Returns:
    pandas.DataFrame: The same DataFrame, but with an additional 'valid_year' column.
    """
    df['valid_year'] = df['year'].isin(list(year_df['year'].astype(str)))
    return df


def remove_invalid_years(df):
    """
    Remove rows with invalid years from a DataFrame.

    This function removes rows from the given DataFrame where the 'valid_year' value is False. 
    It assumes that the DataFrame has a 'valid_year' column which is a boolean flag indicating whether each row's year is valid.

    Parameters:
    df (pandas.DataFrame): A DataFrame containing a 'valid_year' column.

    Returns:
    pandas.DataFrame: A new DataFrame with only the rows where 'valid_year' is True. The index is reset.
    """
    return df[df['valid_year']].reset_index(drop=True)


# load discovery data
print("Loading discovery data...")
data_discovery_root = "datasets/landing-zone/data-discovery"

deaths_source_file = os.path.join(data_discovery_root, 'deaths.csv')
population_source_file = os.path.join(data_discovery_root, 'population.csv')
gini_source_file = os.path.join(data_discovery_root, 'gini.csv')

print("Loading deaths, population, and gini data...")
deaths_df = pd.read_csv(deaths_source_file)
population_df = pd.read_csv(population_source_file)
gini_df = pd.read_csv(gini_source_file)

dfs = [deaths_df, population_df, gini_df]


# load exploitation data through which augmentation will be done
print("Loading exploitation data...")
path_to_exploitation_db = 'datasets/exploitation-zone/exploitation.db'

print("Loading Location data...")
location_query = """
select *
from Location
"""
location_df = execute_query(location_query, path_to_exploitation_db)
location_df['section'] = location_df['section'].astype(str)

print("Loading Year data...")
year_query = """
select distinct(year) 
from Income
"""
year_df = execute_query(year_query, path_to_exploitation_db)


# extract year from time_and_space_obf
print("Extracting year from time_and_space_obf...")
for df in dfs:
    df[['year', 'time_and_space_obf']] = df['time_and_space_obf'].str.extract(r'(.{4})(.*)')


# find most similar rows based on location data
print("Finding most similar rows based on location data...")
location_columns = ['neighborhood_name', 'district_name', 'section']
for df in dfs:
    for loc in location_columns:
        find_most_similar_rows(df, location_df, loc, jaccard_containment_similarity)


# set discard flag for rows that do not match with any location
print("Setting discard flag for rows that do not match with any location...")
for df in dfs:
    df['discard'] = df.apply(lambda row: mark_discard_flag(row, location_df), axis=1)

print(f"Percentage of rows to discard in deaths: {deaths_df[~deaths_df['discard']].shape[0]/len(deaths_df)}")
print(f"Percentage of rows to discard in population: {population_df[~population_df['discard']].shape[0]/len(population_df)}")
print(f"Percentage of rows to discard in gini: {gini_df[~gini_df['discard']].shape[0]/len(gini_df)}")


# set valid year flag
print("Setting valid year flag...")
for df in dfs:
    df = add_valid_year_flag(df)

print(f"Percentage of rows with invalid year in deaths: {deaths_df[~deaths_df['valid_year']].shape[0]/len(deaths_df)}")
print(f"Percentage of rows with invalid year in population: {population_df[~population_df['valid_year']].shape[0]/len(population_df)}")
print(f"Percentage of rows with invalid year in gini: {gini_df[~gini_df['valid_year']].shape[0]/len(gini_df)}")

# Prep data for persisting
print("Preparing data for persisting...")
deaths_df = deaths_df[['NACIONALITAT_PAIS', 'NACIONALITAT_CONTINENT', 'Valor', 'year', 'most_similar_neighborhood_name', 'most_similar_district_name']]
deaths_df = deaths_df.rename(columns={
    'NACIONALITAT_PAIS': 'nationality_country',
    'NACIONALITAT_CONTINENT': 'nationality_continent',
    'Valor': 'value',
    'most_similar_neighborhood_name': 'neighborhood',
    'most_similar_district_name': 'district'
})

population_df = population_df[['Valor', 'NACIONALITAT_G', 'SEXE', 'year', 'most_similar_neighborhood_name', 'most_similar_district_name']]
population_df = population_df.rename(columns={
    'NACIONALITAT_G': 'nationality_continent',
    'Valor': 'value',
    'SEXE': 'gender',
    'most_similar_neighborhood_name': 'neighborhood',
    'most_similar_district_name': 'district'
})

gini_df = gini_df[['Index_Gini', 'year', 'most_similar_neighborhood_name', 'most_similar_district_name']]
gini_df = gini_df.rename(columns={
    'Index_Gini': 'gini_index',
    'most_similar_neighborhood_name': 'neighborhood',
    'most_similar_district_name': 'district'
})

# Persisting data to trusted zone
print("Persisting data to trusted zone...")
path_to_trusted = 'datasets/trusted-zone/trusted.db'
write_data(deaths_df, path_to_trusted, 'deaths')
write_data(population_df, path_to_trusted, 'population')
write_data(gini_df, path_to_trusted, 'gini')
