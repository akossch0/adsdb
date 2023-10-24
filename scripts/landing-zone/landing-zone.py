import shutil
import os
import time


def get_latest_version(target_dir: str, dataset_category: str) -> int:
    """
    Get the latest version number for a dataset category in the target directory.

    Args:
        target_dir (str): Target directory where files are stored.
        dataset_category (str): Descriptive name of the dataset.

    Returns:
        int: The latest version number.
    """
    version_numbers = set()
    for existing_file in os.listdir(target_dir):
        if existing_file.startswith(f"{dataset_category}-"):
            parts = existing_file.split("-")
            if len(parts) == 3 and parts[2].isdigit():
                version_numbers.add(int(parts[2]))

    return max(version_numbers, default=0)


def copy_files_to_persistent(datasets_root: str, dataset_category: str) -> None:
    """
    Copies files from the temporal directory to the persistent directory
    while renaming them according to a specified naming convention.

    Args:
        datasets_root (str): Root folder containing the landing-zone subfolder.
        dataset_category (str): Descriptive name of the dataset.

    Returns:
        None
    """
    source_dir = os.path.join(
        datasets_root, "landing-zone", "temporal", dataset_category
    )

    persistent_dir = os.path.join(datasets_root, "landing-zone", "persistent")

    if not os.path.exists(persistent_dir):
        print(f"Creating folder: {persistent_dir}")
        os.makedirs(persistent_dir)

    target_dir = os.path.join(
        datasets_root, "landing-zone", "persistent", dataset_category
    )

    if not os.path.exists(target_dir):
        print(f"Creating folder: {target_dir}")
        os.makedirs(target_dir)

    timestamp = int(time.time())
    latest_version = get_latest_version(target_dir, dataset_category)

    source_files = os.listdir(source_dir)
    if not source_files:
        print("There are no files to copy")
        return

    for source_file in source_files:
        source_file_path = os.path.join(source_dir, source_file)

        file_extension = os.path.splitext(source_file)[1]

        latest_version += 1
        target_file_name = (
            f"{dataset_category}_{timestamp}_v{latest_version}{file_extension}"
        )
        target_file_path = os.path.join(target_dir, target_file_name)

        print(f"Copying {source_file_path} to {target_file_path}")
        shutil.copy(source_file_path, target_file_path)

    print(f"Copied {len(source_files)} files to {target_dir}")


datasets_root = "datasets"
education_dataset = "education"
income_dataset = "income"
meta_dataset = "meta"

copy_files_to_persistent(datasets_root, education_dataset)
copy_files_to_persistent(datasets_root, income_dataset)
copy_files_to_persistent(datasets_root, meta_dataset)
