import pandas as pd

def transform_data(df, auto_repair=True):
    out = df.copy()
    actions=[]
    before = len(out)
    dup = int(out.duplicated().sum())
    if dup and auto_repair:
        out = out.drop_duplicates()
        actions.append({"action":"Remove exact duplicate rows","affected":dup,"status":"applied"})
    else:
        actions.append({"action":"Duplicate row check","affected":dup,"status":"reported"})
    for col in out.select_dtypes(include="number").columns:
        missing = int(out[col].isna().sum())
        if missing and auto_repair:
            median = out[col].median()
            if pd.notna(median):
                out[col] = out[col].fillna(median)
                actions.append({"action":f"Fill missing {col} with median","affected":missing,"status":"applied"})
        elif missing:
            actions.append({"action":f"Missing values in {col}","affected":missing,"status":"reported"})
    for col in out.select_dtypes(exclude="number").columns:
        missing = int(out[col].isna().sum())
        if missing and auto_repair:
            out[col] = out[col].fillna("Unknown")
            actions.append({"action":f"Fill missing {col} with Unknown","affected":missing,"status":"applied"})
    actions.append({"action":"Rows after ETL","affected":len(out),"status":"complete"})
    return out, actions
