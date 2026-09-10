"""Random split and train-only preprocessing without sklearn."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping,Sequence
import numpy as np
import pandas as pd
from .build_dataset import TARGET_NAME
RANDOM_STATE=42
def random_split(data:pd.DataFrame,seed:int=RANDOM_STATE):
    idx=np.random.default_rng(seed).permutation(len(data)); n=int(len(data)*.70); v=int(len(data)*.15)
    return {"train":data.iloc[idx[:n]].reset_index(drop=True),"validation":data.iloc[idx[n:n+v]].reset_index(drop=True),"test":data.iloc[idx[n+v:]].reset_index(drop=True)}
def assert_random_split(splits:Mapping[str,pd.DataFrame],total:int|None=None):
    if total is not None and sum(map(len,splits.values()))!=total: raise AssertionError("Split does not cover all rows")
    if any(len(v)==0 for v in splits.values()): raise AssertionError("Every split must be non-empty")
@dataclass(frozen=True)
class TrainOnlyPreprocessor:
    numerical_columns:tuple[str,...]; categorical_columns:tuple[str,...]; category_levels:dict[str,tuple[str,...]]; fill_values:dict[str,float]; means:dict[str,float]; stds:dict[str,float]; feature_names:tuple[str,...]
    def transform(self,frame):
        missing=set(self.numerical_columns+self.categorical_columns)-set(frame.columns)
        if missing: raise ValueError(f"Missing feature columns: {sorted(missing)}")
        out={}
        for c in self.numerical_columns:
            v=pd.to_numeric(frame[c],errors="coerce").fillna(self.fill_values[c]).astype(float); out[c]=(v-self.means[c])/self.stds[c]
        for c in self.categorical_columns:
            v=frame[c].astype("string").fillna("__MISSING__")
            for l in self.category_levels[c]: out[f"{c}__{l}"]=(v==l).astype(float)
        result=pd.DataFrame(out,index=frame.index).reindex(columns=self.feature_names,fill_value=0.0).astype(float)
        if not np.isfinite(result.to_numpy()).all(): raise ValueError("Non-finite model input")
        return result
    def metadata(self): return {"numerical_columns":list(self.numerical_columns),"categorical_columns":list(self.categorical_columns),"category_levels":{k:list(v) for k,v in self.category_levels.items()},"feature_names":list(self.feature_names),"fit_scope":"train_only"}
def fit_preprocessor(train_frame,numerical_columns:Sequence[str],categorical_columns:Sequence[str]):
    if TARGET_NAME in set(numerical_columns)|set(categorical_columns): raise ValueError("Target leakage")
    fill={}; means={}; stds={}
    for c in numerical_columns:
        v=pd.to_numeric(train_frame[c],errors="coerce"); med=v.median(); med=0.0 if pd.isna(med) else float(med); f=v.fillna(med); s=float(f.std(ddof=0)); fill[c]=med; means[c]=float(f.mean()); stds[c]=s if np.isfinite(s) and s else 1.0
    levels={c:tuple(sorted(train_frame[c].astype("string").fillna("__MISSING__").unique())) for c in categorical_columns}; names=tuple(numerical_columns)+tuple(f"{c}__{l}" for c in categorical_columns for l in levels[c])
    return TrainOnlyPreprocessor(tuple(numerical_columns),tuple(categorical_columns),levels,fill,means,stds,names)
def transform_splits(preprocessor,splits):
    X={}; y={}
    for name,frame in splits.items(): X[name]=preprocessor.transform(frame).reset_index(drop=True); y[name]=pd.to_numeric(frame[TARGET_NAME],errors="raise").astype(float).reset_index(drop=True)
    return X,y

