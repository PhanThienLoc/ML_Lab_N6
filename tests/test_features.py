import pandas as pd
from src.features import engineer_features
def test_feature_formulas():
    d=pd.DataFrame({"Frequency of Purchases":["Weekly"],"Previous Purchases":[3],"Subscription Status":["Yes"],"Discount Applied":["Yes"],"Promo Code Used":["Yes"],"Review Rating":[4.0],"Item Purchased":["A"],"Category":["C"]})
    x,_=engineer_features(d); assert x.loc[0,"annual_purchase_frequency"]==52; assert x.loc[0,"discount_promo_interaction"]==1
