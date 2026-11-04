from pathlib import Path
import pandas as pd
from .config import BRONZE_DIR, SILVER_DIR, GOLD_DIR

def read_dataset(path):
    p = Path(path)
    if p.suffix.lower() == ".csv":
        return pd.read_csv(p)
    if p.suffix.lower() == ".json":
        return pd.read_json(p)
    if p.suffix.lower() in (".xlsx", ".xls"):
        return pd.read_excel(p)
    raise ValueError(f"Unsupported file type: {p.suffix}")

def save_upload(uploaded):
    safe_name = Path(uploaded.name).name
    target = BRONZE_DIR / safe_name
    target.write_bytes(uploaded.getbuffer())
    return target

def save_layer(df, layer, run_id):
    folder = {"silver": SILVER_DIR, "gold": GOLD_DIR}[layer]
    path = folder / f"{run_id}_{layer}.csv"
    df.to_csv(path, index=False)
    return path

def load_layer(layer):
    folder = {"bronze": BRONZE_DIR, "silver": SILVER_DIR, "gold": GOLD_DIR}[layer]
    files = sorted(folder.glob("*.csv"), key=lambda p: p.stat().st_mtime, reverse=True)
    return pd.read_csv(files[0]) if files else pd.DataFrame()
