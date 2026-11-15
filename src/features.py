import pandas as pd


def build_product_week(clean: pd.DataFrame) -> pd.DataFrame:
    product_week = clean.groupby(
        ["StockCode", "week"], as_index=False
    ).agg(
        units=("Quantity", "sum"),
        invoices=("InvoiceNo", "nunique"),
        n_prices=("UnitPrice", "nunique"),
    )
    weekly_price_counts = (
        clean.groupby(
            ["StockCode", "week", "UnitPrice"], as_index=False
        )
        .size()
        .rename(columns={"size": "price_frequency"})
        .sort_values(
            ["StockCode", "week", "price_frequency", "UnitPrice"],
            ascending=[True, True, False, True],
        )
        .drop_duplicates(["StockCode", "week"])
        .rename(columns={"UnitPrice": "price_mode"})
        [["StockCode", "week", "price_mode"]]
    )
    product_week = product_week.merge(
        weekly_price_counts,
        on=["StockCode", "week"],
        how="left",
        validate="one_to_one",
    )[["StockCode", "week", "units", "invoices", "n_prices", "price_mode"]]
    return product_week.sort_values(
        ["StockCode", "week"], ignore_index=True
    )
