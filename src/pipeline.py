"""End-to-end Customer Shopping Trends data pipeline."""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
from .data_loader import load_raw_data,audit_raw_data,snapshot_raw_files,assert_raw_files_unchanged
from .build_dataset import build_modeling_dataset,TARGET_NAME
from .features import engineer_features,feature_columns
from .preprocessing import random_split,assert_random_split,fit_preprocessor,transform_splits,RANDOM_STATE
def _write_eda(frame, report_dir):
    import matplotlib.pyplot as plt
    out=Path(report_dir)/"figures"; out.mkdir(parents=True,exist_ok=True)
    specs=[("01_sales_amount_distribution.png","Purchase Amount (USD)","hist"),("02_sales_amount_boxplot.png","Purchase Amount (USD)","box"),("03_age_distribution.png","Age","hist"),("04_review_rating_distribution.png","Review Rating","hist"),("05_previous_purchases_distribution.png","Previous Purchases","hist")]
    for name,col,kind in specs:
        fig,ax=plt.subplots(figsize=(7,4)); getattr(frame[col].plot,kind)(ax=ax); ax.set_title(col); fig.tight_layout(); fig.savefig(out/name,dpi=140); plt.close(fig)
    groups=[("06_sales_by_category.png","Category"),("07_sales_by_season.png","Season"),("08_sales_by_discount.png","Discount Applied"),("09_sales_by_promo_code.png","Promo Code Used"),("10_sales_by_frequency.png","Frequency of Purchases")]
    for name,col in groups:
        fig,ax=plt.subplots(figsize=(8,4)); frame.groupby(col)["Purchase Amount (USD)"].mean().sort_values().plot.bar(ax=ax); ax.set_title(f"Mean sales by {col}"); fig.tight_layout(); fig.savefig(out/name,dpi=140); plt.close(fig)
def prepare_data(raw_dir="data/raw",processed_dir="data/processed",report_dir="reports",log_path="logs/data_quality.log"):
    raw_dir,processed_dir,report_dir,log_path=map(Path,(raw_dir,processed_dir,report_dir,log_path)); snap=snapshot_raw_files(raw_dir); raw=load_raw_data(raw_dir); audit=audit_raw_data(raw); base,evidence=build_modeling_dataset(raw); _write_eda(base,report_dir)
    splits_raw=random_split(base,RANDOM_STATE); assert_random_split(splits_raw,len(base))
    train_eng,_=engineer_features(splits_raw["train"],train_frame=splits_raw["train"])
    splits={}; feat_evidence={}
    for name in ("train","validation","test"): splits[name],feat_evidence=engineer_features(splits_raw[name],train_frame=splits_raw["train"])
    nums,cats=feature_columns(); prep=fit_preprocessor(train_eng,nums,cats); X,y=transform_splits(prep,splits)
    processed=pd.concat(splits.values(),ignore_index=True); processed_dir.mkdir(parents=True,exist_ok=True); processed.to_csv(processed_dir/"customer_shopping_trends_features.csv",index=False)
    meta={"dataset":"customer_shopping_trends","aggregation":"current_purchase_record","target":TARGET_NAME,"target_source":"Purchase Amount (USD)","split_method":"random_70_15_15","random_state":RANDOM_STATE,"feature_names":list(prep.feature_names),"source_numerical_features":nums,"source_categorical_features":cats,"preprocessing":prep.metadata(),"rows":len(processed),"raw_audit":audit,"build_evidence":evidence,"feature_evidence":feat_evidence}
    (processed_dir/"preprocessing_metadata.json").write_text(json.dumps(meta,indent=2,ensure_ascii=False),encoding="utf-8")
    Path(log_path).parent.mkdir(parents=True,exist_ok=True); Path(log_path).write_text(json.dumps({"dataset":meta["dataset"],"rows":len(raw),"target":TARGET_NAME,"split_method":meta["split_method"],"raw_sha256":snap.hashes},indent=2),encoding="utf-8")
    Path(report_dir).mkdir(parents=True,exist_ok=True); (Path(report_dir)/"data_analysis.md").write_text(f"Customer Shopping Trends EDA\n\nRows: {len(raw)}. Target: {TARGET_NAME}. Ten figures in reports/figures/.\n",encoding="utf-8")
    assert_raw_files_unchanged(raw_dir,snap)
    return {"X_train":X["train"],"y_train":y["train"],"X_val":X["validation"],"y_val":y["validation"],"X_test":X["test"],"y_test":y["test"],"metadata":meta,"preprocessor":prep,"processed_dataset":processed,"split_frames":splits}

