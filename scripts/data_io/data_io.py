import duckdb
import pandas as pd
import os


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


def load_data(path_to_db: str, table_name: str) -> pd.DataFrame:
    """
    Load a table from a DuckDB database.

    Args:
        path_to_db (str): The path to the DuckDB database.
        table_name (str): The name of the table to load.

    Returns:
        pd.DataFrame: The loaded table.
    """
    con = duckdb.connect(path_to_db)
    if table_exists(con, table_name):
        df = con.sql(f"select * from {table_name}").df()
    else:
        df = pd.DataFrame()
    con.close()
    return df


def overwrite_data(df: pd.DataFrame, path_to_db: str, table_name: str) -> None:
    """
    Save a table to a DuckDB database.

    Args:
        df (pd.DataFrame): The table to save.
        path_to_db (str): The path to the DuckDB database.
        table_name (str): The name of the table to save.
    """
    con = duckdb.connect(path_to_db)
    con.register("df", df)
    if table_exists(con, table_name):
        con.execute(f"DELETE FROM {table_name}")
        con.execute(f"INSERT INTO {table_name} SELECT * FROM df")
    else:
        con.execute(f"CREATE TABLE {table_name} AS SELECT * FROM df")
    con.close()


def copy_to_zone(
    datasets_root: str,
    df: pd.DataFrame,
    create_table_statement: str,
    table_name: str,
    target_zone: str,
) -> None:
    """
    Copy dataframe to the the specified zone in a DuckDB database.

    Args:
        datasets_root (str): The root directory of the datasets.
        df (pd.DataFrame): the dataset to save
        create_table_statement (str): the statement used ot create the table upon first run
        table_name (str): the name of the table to save

    Returns:
        None
    """

    target_dir = os.path.join(datasets_root, target_zone)
    if not os.path.exists(target_dir):
        print(f"Creating folder: {target_dir}")
        os.makedirs(target_dir)

    db_file_path = os.path.join(target_dir, target_zone.split("-")[0] + ".db")
    if not os.path.exists(db_file_path):
        print(f"Creating db file for {target_zone}")
        con = duckdb.connect(db_file_path)
        con.close()  # this should create the file

    con = duckdb.connect(db_file_path)
    con.register("df", df)
    if not table_exists(con, table_name):
        print(f"Table {table_name} does not exist, creating...")
        con.execute(create_table_statement)
        print("Table created; Inserting rows...")
        con.execute(f"INSERT INTO {table_name} SELECT * FROM df")
        print(f"Inserted df rows to {table_name} table")
    else:
        print(f"Overwriting data in {table_name} table")
        con.execute(f"DELETE FROM {table_name}")
        con.execute(f"INSERT INTO {table_name} SELECT * FROM df")
    con.close()
