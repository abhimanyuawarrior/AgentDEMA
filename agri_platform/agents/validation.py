def validate_data(df):
    checks=[]
    checks.append({"check":"Dataset is non-empty","passed":not df.empty,"detail":f"{len(df)} rows"})
    checks.append({"check":"No duplicate rows","passed":not df.duplicated().any(),"detail":f"{int(df.duplicated().sum())} duplicates"})
    missing_pct = float(df.isna().mean().mean()*100) if len(df.columns) else 100.0
    checks.append({"check":"Missing cell ratio below 5%","passed":missing_pct < 5,"detail":f"{missing_pct:.2f}% missing"})
    numeric_ok=True
    for c in df.select_dtypes(include="number").columns:
        if (df[c].dropna().abs() == float("inf")).any():
            numeric_ok=False
    checks.append({"check":"No infinite numeric values","passed":numeric_ok,"detail":"Numeric columns inspected"})
    score = 100 * sum(x["passed"] for x in checks) / max(1,len(checks))
    return {"checks":checks,"score":score}
