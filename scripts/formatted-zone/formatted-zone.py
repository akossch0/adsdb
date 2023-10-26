import os
import duckdb
import pandas as pd
from data_io.data_io import write_data


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

    con = duckdb.connect(db_file_path)
    for source_file in source_files:
        source_file_path = os.path.join(source_dir, source_file)
        dataset_name = os.path.splitext(source_file)[0]
        df = pd.read_csv(source_file_path)
        write_data(df, db_file_path, dataset_name)
    con.close()


datasets_root = "datasets"
education_dataset = "education"
income_dataset = "income"
meta_dataset = "meta"

copy_to_formatted(datasets_root, education_dataset)
copy_to_formatted(datasets_root, income_dataset)
copy_to_formatted(datasets_root, meta_dataset)
