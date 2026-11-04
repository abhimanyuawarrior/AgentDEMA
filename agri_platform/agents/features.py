import pandas as pd

def engineer_features(df):
    out=df.copy()
    actions=[]
    cols={c.lower():c for c in out.columns}
    if "temperature" in cols and "humidity" in cols:
        t,h=cols["temperature"],cols["humidity"]
        out["temperature_humidity_interaction"]=out[t]*out[h]
        actions.append("Created temperature × humidity interaction")
    if "rainfall" in cols and "temperature" in cols:
        r,t=cols["rainfall"],cols["temperature"]
        out["rainfall_temperature_ratio"]=out[r]/out[t].replace(0, pd.NA)
        actions.append("Created rainfall / temperature ratio")
    for c in out.select_dtypes(include="number").columns:
        if out[c].nunique(dropna=True)>10:
            out[f"{c}_zscore"]=(out[c]-out[c].mean())/(out[c].std() or 1)
    return out, actions
