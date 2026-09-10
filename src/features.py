"""Leakage-safe feature engineering for current purchase records."""
from __future__ import annotations
import numpy as np
import pandas as pd
from .build_dataset import FREQUENCY_MAP
def engineer_features(frame: pd.DataFrame, *, train_frame: pd.DataFrame|None=None):
    out=frame.copy()
    out["annual_purchase_frequency"]=out["Frequency of Purchases"].map(FREQUENCY_MAP).fillna(0).astype(float)
    out["log_previous_purchases"]=np.log1p(pd.to_numeric(out["Previous Purchases"],errors="coerce").fillna(0).clip(lower=0))
    out["customer_activity_score"]=out["log_previous_purchases"]*out["annual_purchase_frequency"]
    for s,t in [("Subscription Status","is_subscriber"),("Discount Applied","has_discount"),("Promo Code Used","used_promo_code")]: out[t]=out[s].astype(str).str.lower().eq("yes").astype(float)
    out["discount_promo_interaction"]=out["has_discount"]*out["used_promo_code"]
    fit=train_frame if train_frame is not None else out; global_rating=float(pd.to_numeric(fit["Review Rating"],errors="coerce").mean())
    for s,t in [("Item Purchased","item_purchase_frequency_train"),("Category","category_purchase_frequency_train")]: out[t]=out[s].map(fit[s].value_counts(normalize=True)).fillna(0.0).astype(float)
    for s,t in [("Item Purchased","item_mean_review_rating_train"),("Category","category_mean_review_rating_train")]:
        vals=fit.assign(_rating=pd.to_numeric(fit["Review Rating"],errors="coerce")).groupby(s)["_rating"].mean(); out[t]=out[s].map(vals).fillna(global_rating).astype(float)
    return out, {"frequency_mapping":FREQUENCY_MAP,"popularity_fit_rows":int(len(fit)),"review_rating_fallback":global_rating}
def feature_columns():
    return (["Age","Previous Purchases","annual_purchase_frequency","log_previous_purchases","customer_activity_score","is_subscriber","has_discount","used_promo_code","discount_promo_interaction","item_purchase_frequency_train","category_purchase_frequency_train","item_mean_review_rating_train","category_mean_review_rating_train"],["Gender","Item Purchased","Category","Location","Size","Color","Season","Subscription Status","Payment Method","Shipping Type","Discount Applied","Promo Code Used","Preferred Payment Method","Frequency of Purchases"])

