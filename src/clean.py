from bisect import bisect_left
from pathlib import Path

import pandas as pd

RAW_PATH = Path(__file__).resolve().parents[1] / "data" / "raw" / "Online Retail.xlsx"
PRODUCT_CODE = r"^\d{5}[A-Za-z]*$"   # 5 digits + optional letters, e.g. 85123A


def match_cancelled_orders(raw: pd.DataFrame) -> tuple[pd.Index, pd.Index]:
    """Return matched positive-line and cancellation-line indexes."""
    # Select eligible positive lines and cancellation lines.
    positive_lines = raw.loc[
        raw["Quantity"].gt(0)
        & raw["CustomerID"].notna()
        & raw["InvoiceDate"].notna(),
        ["CustomerID", "StockCode", "Quantity", "InvoiceDate"],
    ]
    cancellation_lines = raw.loc[
        raw["InvoiceNo"].astype(str).str.startswith("C")
        & raw["Quantity"].lt(0)
        & raw["UnitPrice"].gt(0)
        & raw["CustomerID"].notna(),
        ["CustomerID", "StockCode", "Quantity", "InvoiceDate"],
    ].sort_values("InvoiceDate", kind="mergesort")

    # Group and sort possible sales by customer, product, and exact quantity.
    candidates = {}
    for line in positive_lines.itertuples():
        key = (line.CustomerID, line.StockCode, line.Quantity)
        candidates.setdefault(key, []).append((line.InvoiceDate, line.Index))
    candidate_dates = {}
    candidate_indexes = {}
    available_predecessors = {}
    for key, lines in candidates.items():
        lines.sort(key=lambda item: item[0])
        candidate_dates[key] = [line[0] for line in lines]
        candidate_indexes[key] = [line[1] for line in lines]
        available_predecessors[key] = list(range(len(lines) + 1))

    # Match cancellations chronologically to the closest unused earlier line.
    matched_positive_lines = []
    matched_cancellations = []

    def find_available(parent, position):
        root = position
        while parent[root] != root:
            root = parent[root]
        while position != root:
            next_position = parent[position]
            parent[position] = root
            position = next_position
        return root

    for cancellation in cancellation_lines.itertuples():
        if pd.isna(cancellation.InvoiceDate):
            continue
        key = (
            cancellation.CustomerID,
            cancellation.StockCode,
            -cancellation.Quantity,
        )
        if key not in candidates:
            continue
        parent = available_predecessors[key]
        position = find_available(
            parent, bisect_left(candidate_dates[key], cancellation.InvoiceDate)
        )
        if position:
            positive_index = candidate_indexes[key][position - 1]
            matched_positive_lines.append(positive_index)
            matched_cancellations.append(cancellation.Index)
            parent[position] = find_available(parent, position - 1)

    return pd.Index(matched_positive_lines), pd.Index(matched_cancellations)


def load_clean(
    path=RAW_PATH, verbose=True, exclude_matched_cancellations=True
) -> pd.DataFrame:
    # Load the source and normalize product codes before matching.
    raw = pd.read_excel(path, engine="openpyxl")
    raw["StockCode"] = raw["StockCode"].astype(str).str.strip()
    matched_positive, matched_cancellations = match_cancelled_orders(raw)

    # Apply the existing invoice, quantity, price, and product-code filters.
    df = raw[~raw["InvoiceNo"].astype(str).str.startswith("C")]
    df = df[(df["Quantity"] > 0) & (df["UnitPrice"] > 0)]
    df = df[df["StockCode"].str.match(PRODUCT_CODE)]
    if exclude_matched_cancellations:
        # Optionally remove only the matched original positive lines.
        df = df[~df.index.isin(matched_positive)].copy()
    else:
        df = df.copy()

    df["line_value"] = df["Quantity"] * df["UnitPrice"]
    df["week"] = df["InvoiceDate"].dt.to_period("W").dt.start_time

    assert df["Quantity"].gt(0).all()
    assert df["UnitPrice"].gt(0).all()
    assert not df["InvoiceNo"].astype(str).str.startswith("C").any()
    assert df["StockCode"].str.match(PRODUCT_CODE).all()

    if verbose:
        print(f"Matched cancellations: {len(matched_cancellations):,}")
        print("Rows removed by PRODUCT_CODE regex (top 20 StockCodes):")
        excluded_codes = raw.loc[
            ~raw["StockCode"].str.match(PRODUCT_CODE), "StockCode"
        ].value_counts().head(20)
        print(excluded_codes.to_string())
        print(
            f"{len(raw):,} raw rows -> {len(df):,} clean rows, "
            f"{df['StockCode'].nunique():,} products, {df['Quantity'].sum():,} units"
        )
    return df
