import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline

LABEL_CANDIDATES = ["crop", "crop_name", "label", "recommended_crop"]
def recommend_crops(df, inputs, crop_label=None, top_n=5):
    label = crop_label
    if label is None:
        label = next((c for c in df.columns if c.lower() in LABEL_CANDIDATES), None)
    if label and label in df.columns:
        features=[c for c in df.select_dtypes(include="number").columns if c != label]
        train=df[features+[label]].dropna(subset=[label])
        if len(features) and train[label].nunique()>1 and len(train)>=10:
            model=make_pipeline(SimpleImputer(strategy="median"),
                                RandomForestClassifier(n_estimators=150, random_state=42,
                                                       class_weight="balanced"))
            model.fit(train[features],train[label].astype(str))
            row=pd.DataFrame([{c:inputs.get(c, float(train[c].median())) for c in features}])
            probs=model.predict_proba(row)[0]
            classes=model[-1].classes_
            ranked=sorted(zip(classes,probs),key=lambda x:x[1],reverse=True)[:top_n]
            return [{"crop":str(c),"suitability_score":round(float(p)*100,2),
                     "method":"RandomForest baseline"} for c,p in ranked]
    # Transparent fallback: only ranks crops observed in data by frequency.
    crop_col=next((c for c in df.columns if "crop" in c.lower()),None)
    if crop_col:
        counts=df[crop_col].dropna().astype(str).value_counts(normalize=True).head(top_n)
        return [{"crop":c,"suitability_score":round(float(v)*100,2),
                 "method":"Historical frequency baseline — not agronomic suitability"} for c,v in counts.items()]
    return [{"crop":"Insufficient labelled data","suitability_score":0,
             "method":"Provide a crop label column and representative training data"}]
