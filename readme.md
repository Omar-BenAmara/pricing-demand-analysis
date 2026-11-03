# Pricing and recorded quantity

An exploratory analysis of transaction-level data from the UCI Online Retail
dataset. The project investigates how observed unit price relates to recorded
quantity for comparable products, while making transaction filtering and
cancellation matching explicit. Recorded quantity is not verified demand, and
the analysis does not estimate a causal price effect.

## Business questions

- How do cancellations, returns, unusual quantities, and missing customer
  identifiers affect product-level quantity rankings?
- How sensitive are product rankings to line-level outliers and signed
  quantities?
- Within a product, do transactions at different observed prices coincide
  with different recorded quantities, and is there enough persistent price
  variation to support a careful comparison?

The last question remains future work; the current notebooks establish the data
and cleaning foundation rather than a final price-response result.

## Dataset

The source workbook is `data/raw/Online Retail.xlsx`. It contains 541,909
invoice-line records across eight fields, covering 2010-12-01 to 2011-12-09.
The initial profile includes 25,900 invoices, 4,070 stock codes, and 38
countries. `CustomerID` is missing on 135,080 rows. The raw data also includes
negative quantities, zero and negative prices, and cancellation-prefixed
invoice numbers; these are investigated rather than assumed to be ordinary
sales.

## Methodology

1. **Profile the raw data** in `01_data_understanding.ipynb`: inspect schema,
   missingness, transaction classes, and unusual rows without changing the
   source frame.
2. **Investigate rankings and cleaning** in `02_cleaning.ipynb`: compare
   positive-quantity, positive-price product rankings with largest-line
   removal and a separate signed-quantity sensitivity analysis.
3. **Build a reproducible clean population** by excluding `C` invoices,
   non-positive quantity or price, and stock codes that do not match five
   digits plus optional letters. Then remove only positive lines that can be
   matched one-to-one to an earlier cancellation for the same identified
   customer, normalized stock code, and exact quantity.
4. **Diagnose unmatched cancellations** by checking whether larger, equal, or
   smaller eligible earlier purchases exist for the same customer and product.
   These comparisons identify candidates, not proven return links.

The clean-row waterfall is **541,909 → 532,621 → 530,104 → 527,725 → 524,894**.
The final population has 3,786 products and 5,351,288 positive units.
Positive rows with missing `CustomerID` remain in the clean population, but
cannot be used for customer-based cancellation matching. The reusable loader,
stock-code normalization, and matcher are in `src/clean.py`.

## Findings

- StockCode `23843` has an 80,995-unit positive line and an equal cancellation
  for the same customer. StockCode `23166` has 78,033 positive-price units,
  dominated by one 74,215-unit line (95.1%) that also has an exact cancellation
  match. These examples show why raw quantity rankings need transaction
  context.
- Rankings change materially when the largest positive line is removed or
  signed quantities are netted. The result depends on the population
  definition; neither ranking is a verified demand measure.
- The matcher considered 8,905 cancellations: 2,831 matched and 6,074
  unmatched. Of the unmatched lines, 4,572 have a larger eligible earlier
  purchase (23,914 cancellation units), making them possible partial-return
  candidates. That quantity is about 0.45% of clean units, a scale comparison
  rather than a confirmed return rate.
- A further 383 cancellation-prefixed rows have missing `CustomerID` and
  cannot be matched. Of the 1,031 unmatched product-code cancellations with
  no earlier eligible same-customer, same-product purchase in the file, 544
  fall in December 2010 and January 2011 (about 53%). This early-period
  concentration supports, but does not establish, the possibility of pre-file
  purchases.

## Tools

Python, pandas, Jupyter Notebook, openpyxl, and the pinned dependencies in
`requirements.txt`. The notebooks present tabular rankings, waterfall counts,
and matching diagnostics.

## Repository structure

```text
data/raw/Online Retail.xlsx
notebooks/
  01_data_understanding.ipynb
  02_cleaning.ipynb
  archive/                 # superseded notebooks retained for history
src/
  clean.py
requirements.txt
PROJECT_CONTEXT.md
```

## Run the notebooks

From the repository root, create and activate a virtual environment, install
the pinned dependencies, then open Jupyter:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
jupyter lab
```

Run `01_data_understanding.ipynb` and then `02_cleaning.ipynb` from top to
bottom. The notebooks load the workbook from the repository's `data/raw/`
path.

## Status and limitations

Raw-data inspection, ranking sensitivity checks, cleaning, exact cancellation
matching, and unmatched-return diagnostics are complete. Within-product
price/quantity analysis is not yet complete. Next steps are to distinguish
persistent price changes from isolated or special-price lines, then assess
product-specific price/quantity patterns with time and customer composition in
view.

The workbook covers about one year and does not provide stock availability or
unmet demand. A matching rule cannot establish the true business reason for a
cancellation; partial returns are not netted, and purchases before the file
starts are unobserved. Any future price/quantity association should remain
descriptive, not causal.
