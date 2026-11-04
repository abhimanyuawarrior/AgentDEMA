import pandas as pd

def profile_data(df):
    missing = int(df.isna().sum().sum())
    rows, cols = df.shape
    column_profile = pd.DataFrame({
        "column": df.columns,
        "dtype": [str(df[c].dtype) for c in df.columns],
        "missing": [int(df[c].isna().sum()) for c in df.columns],
        "missing_pct": [round(float(df[c].isna().mean()*100), 2) for c in df.columns],
        "unique": [int(df[c].nunique(dropna=True)) for c in df.columns],
    })
    summary = {
        "rows": int(rows), "columns": int(cols), "missing_cells": missing,
        "duplicate_rows": int(df.duplicated().sum()),
        "numeric_columns": df.select_dtypes(include="number").columns.tolist(),
        "categorical_columns": df.select_dtypes(exclude="number").columns.tolist(),
        "memory_mb": round(float(df.memory_usage(deep=True).sum()/1024**2), 3)
    }
    return summary, column_profile
