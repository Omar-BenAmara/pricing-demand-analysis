import pandas as pd
import statsmodels.api as sm


def fit_within_product(data, outcome, extra_regressors=()):
    week_dummies = pd.get_dummies(
        data["week_id"], prefix="week", drop_first=True, dtype=float
    )
    regressor_names = ["log_price", *extra_regressors]
    x = pd.concat([data[regressor_names], week_dummies], axis=1).astype(float)
    grouped = data["StockCode"]
    y_within = data[outcome] - data.groupby("StockCode")[outcome].transform("mean")
    x_within = x - x.groupby(grouped).transform("mean")
    return sm.OLS(y_within, x_within).fit(
        cov_type="cluster",
        cov_kwds={"groups": grouped},
    )
