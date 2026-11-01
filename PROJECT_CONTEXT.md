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
- `notebooks/04_partial_returns.ipynb` — classification of unmatched cancellations

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
- Matcher validated: 6,074 cancellations (of 8,905 considered) are unmatched after
  2,831 exact matches. Notebook 04 splits them into 5 groups:
  4,572 larger earlier purchase (partial-return candidates, 23,914 units);
  21 equal earlier purchase, all already used by another cancellation (no bug);
  84 only smaller earlier purchases;
  1,031 no earlier purchase, product code;
  366 no earlier purchase, non-product code (POST, D, etc.).
- Partial returns are about 0.45% of clean units (23,914 of 5,351,288).
  Decision: no netting function now; documented as a limitation.
- Dec 2010 + Jan 2011 hold 53% (544) of the 1,031 "no earlier purchase" group
  but only 18% (1,078) of all unmatched cancellations. This supports the idea
  that these are returns of sales before the file starts (supported, not proven).
- This group does not contaminate the clean data: no original sale is in the file.

## Decisions and rationale

- StockCode is normalized in one loader, `load_raw()`, used by notebooks 02 and 03.
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
- no partial-return netting for now (about 0.45% of units); documented as a limitation.

## Current state

Cancellation-matching topic is closed. Next: within-product price variation,
separately for rows with and without CustomerID; define what counts as real
price variation (over time) versus noise.

## Working method (how we decide)

1. State one question. 2. Choose population and unit. 3. Bounded Copilot prompt
(change only named files, report failed assertions, never edit them to pass).
4. Validate with a second independent calculation. 5. Interpret: observation vs
meaning vs limits. 6. One next step. Check which population each number uses
(an earlier wrong count, 6,010, came from the old matcher; correct is 6,074).

## Git habits

VS Code changes the kernel label in notebooks (Python 3 -> .venv (3.12.10)).
Check `git diff`, restore that noise, add files by name, never `git add .`.
Use `git --no-pager` to avoid the pager.

## Open issues and next action

Cancellation matching is closed. The exact rule is validated (see Verified
findings). Known limits, documented and not fixed:

- Partial returns (about 4,572 cancellation lines, 23,914 units, 0.45% of clean
  units) are not netted. Candidates only; the link to a purchase is not proven.
- 84 cancellations are larger than any single earlier purchase; 21 are second
  cancellations of an already-used purchase.
- Returns without an earlier sale (1,031 product-code lines) are mostly explained
  by sales before the file starts (supported, not proven). They do not
  contaminate the clean data.
- 383 cancellation lines with missing CustomerID cannot be matched.
- Recorded quantity is not verified demand. The file has only one year.

Next action: examine within-product price variation separately for rows with a
CustomerID and rows without one. First define what counts as real price
variation (a price that holds over a period of time) versus noise (single odd
lines, bulk or special prices). Then check whether comparable price and
quantity observations can be defined for a limited set of products.

