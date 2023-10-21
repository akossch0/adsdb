import os
import duckdb
import pandas as pd


def table_exists(con, table_name: str) -> bool:
    """
    Check if a table exists in the DuckDB database.

    Args:
        con (duckdb.Connection): The DuckDB database connection.
        table_name (str): The name of the table to check.

    Returns:
        bool: True if the table exists, False otherwise.
    """
    try:
        con.table(table_name)
        return True
    except duckdb.CatalogException:
        return False


def copy_to_formatted(datasets_root: str, dataset_category: str) -> None:
    """
    Copy CSV files from the landing zone to the formatted zone in a DuckDB database.

    Args:
        datasets_root (str): The root directory of the datasets.
        dataset_category (str): The category of the dataset to copy.

    Returns:
        None
    """

    source_dir = os.path.join(
        datasets_root, "landing-zone", "persistent", dataset_category
    )
    if not os.path.exists(source_dir):
        print(
            f"No such dataset category as {dataset_category} in the persistent landing zone"
        )
        return

    source_files = os.listdir(source_dir)
    if not source_files:
        print("There are no files to copy")
        return

    target_dir = os.path.join(datasets_root, "formatted-zone")
    if not os.path.exists(target_dir):
        print(f"Creating folder: {target_dir}")
        os.makedirs(target_dir)

    db_file_path = os.path.join(target_dir, "formatted.db")
    if not os.path.exists(db_file_path):
        print("Creating db file for formatted zone")
        con = duckdb.connect(db_file_path)
        con.close()  # this should create the file

    con = duckdb.connect(db_file_path)
    for source_file in source_files:
        source_file_path = os.path.join(source_dir, source_file)
        dataset_name = os.path.splitext(source_file)[0]
        df = pd.read_csv(source_file_path)
        if not table_exists(con, dataset_name):
            print(
                f"Table {dataset_name} does not exist, creating from df with {len(df)} rows..."
            )
            con.execute(f"CREATE TABLE {dataset_name} AS SELECT * FROM df")
        else:
            print(f"Overwriting dataset in table {dataset_name}")
            con.execute(f"DELETE FROM {dataset_name}")
            con.execute(f"INSERT INTO {dataset_name} AS SELECT * FROM df")
    con.close()


datasets_root = "datasets"
education_dataset = "education"
income_dataset = "income"
meta_dataset = "meta"

copy_to_formatted(datasets_root, education_dataset)
copy_to_formatted(datasets_root, income_dataset)
copy_to_formatted(datasets_root, meta_dataset)
