from dataset import MainDataset, MetaDataset, OutlierRemovalMode
from helper_functions import fix_valor_column

datasets_root_folder = "datasets"
path_to_formatted_db = "datasets/formatted-zone/formatted.db"

education_dataset_category = "education"
education_important_columns = {"targets": ["Valor"], "type": "NIV_EDUCA_esta"}
education_outlier_removal_mode = OutlierRemovalMode.UNI
education_dataset = MainDataset(
    dataset_category=education_dataset_category,
    path_to_source_db=path_to_formatted_db,
    important_columns=education_important_columns,
    outlier_removal_mode=education_outlier_removal_mode,
    path_to_datasets_root=datasets_root_folder,
    cleaning_function=fix_valor_column,
)

income_dataset_category = "income"
income_important_columns = {
    "targets": ["Total"],
    "type": "Indicadores de renta media y mediana",
}
income_outlier_removal_mode = OutlierRemovalMode.UNI
income_dataset = MainDataset(
    dataset_category=income_dataset_category,
    path_to_source_db=path_to_formatted_db,
    important_columns=income_important_columns,
    outlier_removal_mode=income_outlier_removal_mode,
    path_to_datasets_root=datasets_root_folder,
)

main_datasets = [education_dataset, income_dataset]
for dataset in main_datasets:
    print("-" * 100)
    headline = f"Dataset: {dataset.dataset_category}".upper()
    len_of_sides = (100 - len(headline)) // 2
    print(len_of_sides * "-" + headline + len_of_sides * "-")
    print("-" * 100)
    dataset.load_formatted_data()
    try:
        dataset.merge_dfs()
    except Exception as e:
        print(e)
        print(f"Shutting down due to error in {dataset.dataset_category} dataset")
        exit()
    print(dataset.df.head())
    dataset.perform_eda()
    dataset.perform_data_quality_processes()
    dataset.copy_to_trusted()

meta_dataset_category = "meta"
meta_dataset = MetaDataset(
    dataset_category=meta_dataset_category,
    path_to_source_db=path_to_formatted_db,
    path_to_datasets_root=datasets_root_folder,
)
print("-" * 100)
headline = f"Dataset: {meta_dataset.dataset_category}".upper()
len_of_sides = (100 - len(headline)) // 2
print(len_of_sides * "-" + headline + len_of_sides * "-")
print("-" * 100)
meta_dataset.load_formatted_data()
meta_dataset.merge_dfs()
meta_dataset.perform_eda()
meta_dataset.perform_data_quality_processes()
meta_dataset.copy_to_trusted()
