from src.preprocessing import random_split,assert_random_split,fit_preprocessor,transform_splits
from src.features import engineer_features,feature_columns
from src.build_dataset import build_modeling_dataset
from src.data_loader import load_raw_data
def test_random_split_and_train_only_schema():
    d,_=build_modeling_dataset(load_raw_data("data/raw")); s=random_split(d); assert_random_split(s,len(d))
    allx={}
    for n in s: allx[n],_=engineer_features(s[n],train_frame=s["train"])
    a,b=feature_columns(); p=fit_preprocessor(allx["train"],a,b); X,y=transform_splits(p,allx); assert list(X["train"].columns)==list(X["test"].columns)

