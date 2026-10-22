from pathlib import Path
import pandas as pd

RAW_PATH = Path(__file__).resolve().parents[1] / "data" / "raw" / "Online Retail.xlsx"
PRODUCT_CODE = r"^\d{5}[A-Za-z]*$"   # 5 digits + optional letters, e.g. 85123A


def find_reversed_products(raw: pd.DataFrame, min_gross=500, max_return_rate=0.9) -> list:
    """Products whose recorded purchases are almost fully cancelled by returns."""
    priced = raw[raw["UnitPrice"] > 0]
    gross = priced.loc[priced["Quantity"] > 0].groupby("StockCode")["Quantity"].sum()
    returned = -priced.loc[priced["Quantity"] < 0].groupby("StockCode")["Quantity"].sum()
    rate = returned.reindex(gross.index).fillna(0) / gross
    return rate[(rate > max_return_rate) & (gross >= min_gross)].index.tolist()


def load_clean(path=RAW_PATH, verbose=True) -> pd.DataFrame:
    raw = pd.read_excel(path, engine="openpyxl")
    raw["StockCode"] = raw["StockCode"].astype(str).str.strip()
    reversed_codes = find_reversed_products(raw)

    df = raw[~raw["InvoiceNo"].astype(str).str.startswith("C")]
    df = df[(df["Quantity"] > 0) & (df["UnitPrice"] > 0)]
    df = df[df["StockCode"].str.match(PRODUCT_CODE)]
    df = df[~df["StockCode"].isin(reversed_codes)].copy()

    df["line_value"] = df["Quantity"] * df["UnitPrice"]
    df["week"] = df["InvoiceDate"].dt.to_period("W").dt.start_time

    assert (df["Quantity"] > 0).all() and (df["UnitPrice"] > 0).all()
    assert df["StockCode"].str.match(PRODUCT_CODE).all()
    assert not df["StockCode"].isin(reversed_codes).any()

    if verbose:
        print("Reversed products dropped:", reversed_codes)
        print(f"{len(raw):,} raw rows -> {len(df):,} clean rows, "
              f"{df['StockCode'].nunique():,} products, {df['Quantity'].sum():,} units")
    return df
