import pandas as pd
from src.data_loader import REQUIRED_COLUMNS,load_raw_data
from src.build_dataset import build_modeling_dataset,TARGET_NAME
from src.pipeline import prepare_data
def test_schema_and_target():
    d=load_raw_data("data/raw"); assert list(d.columns)==REQUIRED_COLUMNS; m,e=build_modeling_dataset(d); assert TARGET_NAME in m and len(m)==3900
def test_pipeline_artifacts():
    p=prepare_data("data/raw","data/processed","reports","logs/data_quality.log"); assert len(p["y_train"])+len(p["y_val"])+len(p["y_test"])==3900

