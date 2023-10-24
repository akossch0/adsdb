import pandas as pd
import numpy as np


def compare_dataframe_schemas(
    df1: pd.DataFrame, df2: pd.DataFrame, table_name1: str, table_name2: str
) -> bool:
    # Compare column count
    if len(df1.columns) != len(df2.columns):
        print(
            f"Column count is different. {table_name1} has {len(df1.columns)} columns, while {table_name2} has {len(df2.columns)} columns."
        )
        return False

    # Compare column names
    if list(df1.columns) != list(df2.columns):
        print("Column names differ:")
        diff_columns = set(df1.columns).symmetric_difference(set(df2.columns))
        print(diff_columns)
        return False

    # Compare data types
    for column in df1.columns:
        if df1[column].dtype != df2[column].dtype:
            print(
                f"Data type for column '{column}' differs. {table_name1} has type {df1[column].dtype}, while {table_name2} has type {df2[column].dtype}."
            )
            return False
    return True


# tukeys method (univariate)
def tm_outliers(df: pd.DataFrame, variable: str, strict: bool) -> list:
    # Calculate descriptive statistics for the variable of interest
    desc_stats = df[variable].describe()

    # Extract quartiles and IQR from the descriptive statistics
    q1, q3 = desc_stats[["25%", "75%"]]
    iqr = q3 - q1

    # Calculate inner and outer fences
    inner_fence = 1.5 * iqr
    outer_fence = 3 * iqr

    inner_fence_le, inner_fence_ue = q1 - inner_fence, q3 + inner_fence
    outer_fence_le, outer_fence_ue = q1 - outer_fence, q3 + outer_fence

    # Identify outliers
    outliers_prob = df[
        (df[variable] <= outer_fence_le) | (df[variable] >= outer_fence_ue)
    ].index
    outliers_poss = df[
        (df[variable] <= inner_fence_le) | (df[variable] >= inner_fence_ue)
    ].index

    # Return results
    if outliers_prob.empty and outliers_poss.empty:
        return list()
    elif strict == 1:
        return list(outliers_prob)
    elif strict == 0:
        return list(outliers_poss)


def fix_valor_column(df: pd.DataFrame) -> pd.DataFrame:
    df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce").fillna(np.nan)
    return df
