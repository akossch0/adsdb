from enum import Enum
import os
from abc import ABC, abstractmethod
import pandas as pd
import duckdb
from sklearn.impute import SimpleImputer
import numpy as np
from pyod.models.knn import KNN
from helper_functions import compare_dataframe_schemas, tm_outliers
from data_io.data_io import table_exists


class OutlierRemovalMode(Enum):
    UNI = 1
    MULTI = 2
    BOTH = 3
    NONE = 4


class Dataset(ABC):
    def __init__(
        self,
        dataset_category: str,
        path_to_source_db: str,
        important_columns: dict,
        outlier_removal_mode: OutlierRemovalMode,
        path_to_datasets_root: str,
        cleaning_function=None,
    ) -> None:
        self.dataset_category: str = dataset_category
        self.path_to_source_db: str = path_to_source_db
        self.important_columns: dict = important_columns
        self.outlier_removal_mode: OutlierRemovalMode = outlier_removal_mode
        self.path_to_datasets_root: str = path_to_datasets_root
        self.cleaning_function = cleaning_function
        self.table_name_df_tuples: list = None
        self.df: pd.DataFrame = None
        self.stripped_df: pd.DataFrame = None
        self.uni_outliers: dict = None
        self.multi_outliers = None

    @abstractmethod
    def perform_data_quality_processes(self) -> None:
        pass

    def load_formatted_data(self) -> None:
        print(f"Loading formatted data for {self.dataset_category}...")
        con = duckdb.connect(self.path_to_source_db)
        tables = con.sql("show all tables").df()
        table_names = set(
            [
                table
                for table in tables["name"]
                if table.startswith(self.dataset_category)
            ]
        )

        self.table_name_df_tuples = [
            (table_name, con.sql(f"select * from {table_name}").df())
            for table_name in table_names
        ]
        con.close()
        print(f"Loaded {len(self.table_name_df_tuples)} table(s)")

    def perform_eda(self) -> None:
        if self.df is None:
            print("Dataframe not initialized yet, cannot perform eda.")
            return

        print("Types:")
        print(self.df.info())

        print("Basic Statistics:")
        print(self.df.describe())

        print("\nMissing Values:")
        print(self.df.isnull().sum())

        print("\nUnique Values:")
        for column in self.df.columns:
            unique_values = self.df[column].unique()
            num_unique = len(unique_values)
            print(f"{column}: {num_unique} unique values")
            if num_unique < 10:
                print(unique_values)
            else:
                print("Too many unique values to display")

    def __mergeability_condition(self) -> bool:
        if len(self.table_name_df_tuples) == 1:
            return True

        mergeable = True
        for df_i in self.table_name_df_tuples:
            for df_j in self.table_name_df_tuples:
                if df_i[0] != df_j[0]:
                    if not compare_dataframe_schemas(
                        df_i[1], df_j[1], df_i[0], df_j[0]
                    ):
                        mergeable = False
        return mergeable

    def merge_dfs(self):
        mergeable = self.__mergeability_condition()
        if not mergeable:
            raise Exception(
                f"Can not merge formatted tables of {self.dataset_category}"
            )
        if len(self.table_name_df_tuples) == 1:
            self.df = self.table_name_df_tuples[0][1]
            self.__strip_df()
            return
        list_of_dfs = [i[1] for i in self.table_name_df_tuples]
        self.df = pd.concat(list_of_dfs, ignore_index=True)
        # additional cleaning
        if self.cleaning_function is not None:
            self.df = self.cleaning_function(self.df)

        self.__strip_df()

    def __strip_df(self) -> None:
        if (
            "targets" not in self.important_columns
            or len(self.important_columns["targets"]) != 1
        ):
            self.stripped_df = self.df
            return
        self.stripped_df = self.df[self.important_columns["targets"]]

    def _perform_deduplication(self) -> None:
        headline = 20 * "-" + "Deduplication" + 20 * "-"
        print(headline)
        duplicate_rows = self.df.duplicated()
        num_duplicates = duplicate_rows.sum()
        print("Number of duplicate rows:", num_duplicates)
        if num_duplicates > 0:
            print("Duplicate rows:")
            print(self.df[duplicate_rows])
            print("Removing duplicates...")
            self.df.drop_duplicates(inplace=True, ignore_index=False)
            print("Removed duplicates")
        print(len(headline) * "-")

    def _find_uni_outliers(self, strict: bool) -> None:
        types = self.df[self.important_columns["type"]].unique()
        targets = self.important_columns["targets"]
        self.uni_outliers = dict()
        for t in types:
            for target in targets:
                self.uni_outliers[str(t) + "_" + str(target)] = tm_outliers(
                    self.df[self.df[self.important_columns["type"]] == t],
                    target,
                    strict,
                )
        return self.uni_outliers

    def _summarize_uni_outliers(self) -> None:
        for var in self.uni_outliers.keys():
            outliers = [o for o in self.uni_outliers[var]]
            print(
                f"{len(outliers)} out of {len(self.df)} samples were univariate outliers of {var} variable in the {self.dataset_category} data"
            )

    def _find_multi_outliers(self) -> None:
        if len(self.important_columns["targets"]) == 1:
            return
        self.multi_outliers = []
        types = self.df[self.important_columns["type"]].unique()
        for t in types:
            df = self.stripped_df[self.stripped_df[self.important_columns["type"]] == t]
            # NaN values temporarily imputed by mean
            imputer = SimpleImputer(missing_values=np.nan, strategy="mean")
            imputer = imputer.fit(df.copy())
            imputed_df = imputer.transform(df.copy().values)
            clf = KNN()
            clf.fit(imputed_df)
            outliers = clf.predict(imputed_df)
            outliers = outliers.astype(bool)
            outliers = np.invert(outliers)
            self.multi_outliers.append(outliers)
        return self.multi_outliers

    def _summarize_multi_outliers(self) -> None:
        if len(self.stripped_df.columns) == 1:
            print(
                "There is only one column, no need for multivariate outlier detection"
            )
            return
        nr_mv_outliers = len([o for o in self.multi_outliers if not o])
        print(
            f"{nr_mv_outliers} out of {len(self.multi_outliers)} samples are multivariate outliers in {self.dataset_category} dataset"
        )

    def __remove_uni_outliers(self) -> None:
        outliers = [item for sublist in self.uni_outliers.values() for item in sublist]
        self.df.drop(outliers, inplace=True)

    def __remove_multi_outliers(self) -> None:
        self.df = self.df[self.multi_outliers]

    def _remove_outliers(self) -> None:
        headline = 20 * "-" + "Outlier removal" + 20 * "-"
        print(headline)
        starting_size = len(self.df)
        if self.outlier_removal_mode == OutlierRemovalMode.NONE:
            print("No outlier will be removed.")
        elif self.outlier_removal_mode == OutlierRemovalMode.UNI:
            print("Removing univariate outliers")
            self.__remove_uni_outliers()
        elif self.outlier_removal_mode == OutlierRemovalMode.MULTI:
            print("Removing multivariate outliers")
            self.__remove_multi_outliers()
        print(f"Removed {starting_size - len(self.df)} out of {starting_size} rows")
        print(len(headline) * "-")

    def copy_to_trusted(self) -> None:
        target_dir = os.path.join(self.path_to_datasets_root, "trusted-zone")
        if not os.path.exists(target_dir):
            print(f"Creating folder: {target_dir}")
            os.makedirs(target_dir)

        db_file_path = os.path.join(target_dir, "trusted.db")
        if not os.path.exists(db_file_path):
            print("Creating db file for trusted zone")
            con = duckdb.connect(db_file_path)
            con.close()  # this should create the file

        con = duckdb.connect(db_file_path)
        df_to_save = self.df
        if not table_exists(con, self.dataset_category):
            print(
                f"Table {self.dataset_category} does not exist, creating with {len(df_to_save)} rows..."
            )
            con.execute(
                f"CREATE TABLE {self.dataset_category} AS SELECT * FROM df_to_save"
            )
            print("Saved dataset to table")
        else:
            print("Overwriting dataset in table")
            con.execute(f"DROP TABLE {self.dataset_category}")
            con.execute(
                f"CREATE TABLE {self.dataset_category} AS SELECT * FROM df_to_save"
            )
        con.close()


class MainDataset(Dataset):
    def __init__(
        self,
        dataset_category: str,
        path_to_source_db: str,
        important_columns: dict,
        outlier_removal_mode: OutlierRemovalMode,
        path_to_datasets_root: str,
        cleaning_function=None,
    ) -> None:
        super().__init__(
            dataset_category,
            path_to_source_db,
            important_columns,
            outlier_removal_mode,
            path_to_datasets_root,
            cleaning_function,
        )

    def perform_data_quality_processes(self) -> None:
        self._perform_deduplication()
        self._find_uni_outliers(strict=True)
        self._summarize_uni_outliers()
        self._find_multi_outliers()
        self._summarize_multi_outliers()
        self._remove_outliers()


class MetaDataset(Dataset):
    def __init__(
        self, dataset_category: str, path_to_source_db: str, path_to_datasets_root: str
    ) -> None:
        super().__init__(
            dataset_category,
            path_to_source_db,
            important_columns={},
            outlier_removal_mode=OutlierRemovalMode.NONE,
            path_to_datasets_root=path_to_datasets_root,
        )

    def perform_data_quality_processes(self) -> None:
        self._perform_deduplication()
