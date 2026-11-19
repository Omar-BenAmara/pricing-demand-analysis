# Pricing and recorded quantity

This project uses the UCI Online Retail workbook to describe transaction
patterns, clean a reproducible population, investigate weekly price variation,
and estimate within-product associations between weekly modal price and
recorded quantities. Interpret the results as association, not causal;
recorded quantity is not verified demand.

## Current notebook workflow

Run the notebooks from the repository root in this order:

1. [`notebooks/01_data_understanding.ipynb`](notebooks/01_data_understanding.ipynb)
   profiles the raw workbook and investigates transaction types and anomalies.
2. [`notebooks/02_cleaning.ipynb`](notebooks/02_cleaning.ipynb) compares raw
   product rankings, builds the clean population, matches exact cancellations,
   and screens unmatched cancellations for possible partial-return candidates.
3. [`notebooks/03_price_variation.ipynb`](notebooks/03_price_variation.ipynb)
   aggregates clean lines to product-weeks and describes mixed prices,
   deviations from reference prices, and price/quantity associations.
4. [`notebooks/04_elasticity.ipynb`](notebooks/04_elasticity.ipynb) defines
   product-week samples and estimates product- and week-adjusted associations.
5. [`notebooks/05_price_tiers.ipynb`](notebooks/05_price_tiers.ipynb) compares
   price ratios and within-product estimates by CustomerID status.

`notebooks/archive/` contains superseded notebooks and is not part of the
current run order.

## Data and cleaning

The source is `data/raw/Online Retail.xlsx`. The raw workbook has 541,909
invoice-line rows across eight fields, dated 2010-12-01 through 2011-12-09.
The initial profile reports 25,900 invoices, 4,070 stock codes, 38 countries,
and 135,080 rows with missing `CustomerID`.

The clean-data workflow excludes `C` invoices, keeps positive quantity and
price, keeps product-like stock codes matching five digits with optional
letters, then removes only positive lines matched one-to-one to an earlier
cancellation for the same identified customer, stock code, and exact
quantity. Positive lines with missing `CustomerID` remain in the clean
population but cannot be matched by customer.

The printed row waterfall is **541,909 → 532,621 → 530,104 → 527,725 →
524,894**. The clean population has 3,786 products and 5,351,288 units.
Of 8,905 cancellation lines considered, 2,831 matched and 6,074 did not.
Among unmatched cancellations, 4,572 have a larger eligible earlier purchase
(23,914 cancellation units); these are candidates, not confirmed partial
returns.

## Completed analyses and printed results

- **Weekly price variation:** the product-week table has 100,068 rows.
  46,112 (46.08%) contain multiple recorded prices, accounting for 4,267,571
  units. In 38,453 of those 46,112 product-weeks (83.39%), median line
  quantity is larger at the lowest price than at the highest price.
- **Final model choice:** within-product OLS with week effects
  (`src.models.fit_within_product`) on Sample E. The headline `log_invoices`
  coefficient is -0.397409 (clustered SE 0.014191). Across the invoice models
  in Sections 5-8, coefficients range from -0.493071 (Section 8, Sample E
  restricted to `mode_share_units >= 0.9`) to -0.311295 (Section 6,
  `E-invoices-mode-share`).
- **Units and order size:** in Sample E, the `log_units` coefficient is
  -1.502479 (clustered SE 0.024650). In the Sample B decomposition,
  `log_invoices` is -0.332338 (0.044845), while `log_units_per_invoice` is
  -1.165481 (0.048999). The stronger association is with units per invoice,
  i.e. order size; these two components sum to the Sample B `log_units`
  coefficient of -1.497819.
- **CustomerID price patterns:** among 517,559 qualifying lines, 128,801 have
  missing CustomerID and 388,758 have a recorded CustomerID. Across quantity
  buckets, median price ratios are 1.000 for the identified group and 1.920
  to 2.000 for the missing-ID group. This is evidence of distinct price
  patterns, not proof of non-overlapping tiers; interpreting missing IDs as a
  retail tier remains a hypothesis. The within-product `log_invoices`
  coefficients are -0.493074 for identified lines and -0.494630 for missing
  CustomerID lines.

## Reusable code

- `src/clean.py` provides raw/clean loaders, stock-code normalization, and
  one-to-one cancellation matching.
- `src/features.py` builds the product-week feature table, including units,
  invoice counts, distinct prices, and the modal price.
- `src/models.py` provides `fit_within_product`, which demeans by product,
  includes week effects, and clusters standard errors by `StockCode`.

## Setup and execution

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
jupyter lab
```

Run notebooks 01 through 05 from top to bottom. The analysis is limited to
recorded transactions: zero-sales weeks are absent, weekly modal prices can
mix the identified and missing-CustomerID price patterns and hide
transaction-level variation, the workbook does not report stock availability
or costs, and recorded quantity is not verified demand. These estimates are
association, not causal. Further work would need data and a design that
address these limitations.
