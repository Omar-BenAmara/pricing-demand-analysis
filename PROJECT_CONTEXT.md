# Project context

## Objective

Explore how observed unit price relates to recorded quantity for comparable
products in the Online Retail dataset. This is descriptive analysis, not a
causal estimate of demand.

## Repository structure

- `data/raw/Online Retail.xlsx` — source workbook
- `notebooks/01_data_understanding.ipynb` — raw-data inspection
- `notebooks/03_clean_foundation.ipynb` — matching rule, clean population, and diagnostics
- `notebooks/02_product_analysis.ipynb` — product rankings and sensitivity checks
- `notebooks/archive/02_product_analysis_draft.ipynb` — unchanged earlier analysis
- `src/clean.py` — reusable cleaning and exact cancellation matching
- `requirements.txt` — Python dependencies

## Dataset facts

The workbook has 541,909 invoice-line rows covering 2010-12-01 through
2011-12-09. It contains invoice, stock code, quantity, unit price, customer,
description, date, and country fields. Customer IDs are missing on some rows.

## Verified findings

- StockCode `23843` has a positive 80,995-unit row on invoice `581483` and an
  equal -80,995-unit cancellation on `C581484`, for the same customer.
- StockCode `23166` has a 74,215-unit positive line out of 78,033 positive-price
  units. The exact rule matches five eligible positive lines for this code
  (74,215, 240, 1, 12, and 12 units), each to an earlier cancellation for the
  same customer. Thus the exact rule removes more than the 74,215-unit line
  alone; it removes 265 additional units across four other matched lines.
- StockCode `84347` has a -9,360 return dated 2010-12-02 for CustomerID 15838.
  Ten earlier positive rows for this stock code are in the file, but none is
  for that customer; its original sale is before the dataset's start.

## Decisions and rationale

- Gross product rankings use rows with `Quantity > 0` and `UnitPrice > 0`;
  these are recorded positive quantities, not verified completed sales.
- Net signed quantity is a separate sensitivity measure: it includes positive
  and negative quantities but only rows with `UnitPrice > 0`. It is not mixed
  with gross rankings.
- Cleaning removes a positive line only when a cancellation can be matched
  one-to-one to an earlier positive line for the same customer and stock code
  with exactly the same absolute quantity. Of available candidates, the closest
  earlier line is used. This replaces product-level return-rate thresholds,
  which removed normal sales along with unusual transactions.
- Existing exclusions remain: cancellation invoices, non-positive quantities,
  non-positive unit prices, and stock codes outside the product-code pattern.
  Missing-customer rows remain in the clean data but cannot be matched.

## Current state

Notebook 01 inspects raw rows without modifying them. Notebook 03 applies the
explicit line-level matching rule and reports clean-population checks. Notebook
02 examines raw positive-population rankings, cancellations, and sensitivity
to largest-line removal and net signed quantities. The current clean population
has 524,894 rows, 3,895 products, and 5,351,288 positive units. In that
population, 3,349 of 3,895 products have multiple observed prices; the counts
are 2,618 of 3,645 for rows with CustomerID and 2,730 of 3,388 for rows without
CustomerID.

## Open issues and next action

Exact matching does not identify partial cancellations, changed quantities,
returns with missing customer IDs, or other unmatched relationships. The
dataset also omits sales before its start and does not establish whether a
recorded quantity is actual demand. The next analysis should examine within-
product price variation separately for rows with a customer ID and rows with a
missing customer ID, then assess whether comparable price/quantity observations
can be defined.
