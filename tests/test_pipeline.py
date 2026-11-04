import pandas as pd
from agri_platform.agents.profiling import profile_data
from agri_platform.agents.etl import transform_data
from agri_platform.agents.validation import validate_data

def test_profile_counts():
    df=pd.DataFrame({"rainfall":[10,None,20],"crop":["rice","rice","wheat"]})
    profile,_=profile_data(df)
    assert profile["rows"] == 3
    assert profile["missing_cells"] == 1

def test_etl_repairs_missing_and_duplicates():
    df=pd.DataFrame({"rainfall":[10,None,10],"crop":["rice","wheat","rice"]})
    cleaned,actions=transform_data(df,True)
    assert not cleaned.duplicated().any()
    assert cleaned["rainfall"].isna().sum() == 0

def test_validation_score():
    df=pd.DataFrame({"x":[1,2,3]})
    assert validate_data(df)["score"] == 100
