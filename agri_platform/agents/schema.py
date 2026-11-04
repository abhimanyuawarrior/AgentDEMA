import re
ALIASES = {
    "nitrogen": ["n", "nitrogen", "soil_n", "nitrogen_content"],
    "phosphorus": ["p", "phosphorus", "phosphorous", "soil_p"],
    "potassium": ["k", "potassium", "soil_k"],
    "ph": ["ph", "soil_ph", "ph_value"],
    "temperature": ["temperature", "temp", "avg_temp"],
    "humidity": ["humidity", "relative_humidity"],
    "rainfall": ["rainfall", "rain", "precipitation"],
    "crop": ["crop", "crop_name", "label", "recommended_crop"],
    "yield": ["yield", "crop_yield", "production"]
}
def normalize(s):
    return re.sub(r"[^a-z0-9]+", "_", str(s).strip().lower()).strip("_")
def map_schema(columns):
    rows=[]
    for col in columns:
        key=normalize(col)
        target, confidence = key, 0.45
        for canonical, aliases in ALIASES.items():
            if key in aliases:
                target, confidence = canonical, 0.99
                break
            if any(a in key for a in aliases if len(a)>2):
                target, confidence = canonical, 0.78
                break
        rows.append({"source_column": col, "suggested_column": target,
                     "confidence": confidence, "review_required": confidence < 0.8})
    return rows
