from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
BRONZE_DIR = DATA_DIR / "bronze"
SILVER_DIR = DATA_DIR / "silver"
GOLD_DIR = DATA_DIR / "gold"
for folder in (BRONZE_DIR, SILVER_DIR, GOLD_DIR):
    folder.mkdir(parents=True, exist_ok=True)
