# Project context

## Objective

Explore how observed unit price relates to recorded quantity for comparable
products in the UCI Online Retail data. This is descriptive analysis, not a
causal estimate of demand: recorded quantities are not verified demand or
necessarily completed sales.

## Data

`data/raw/Online Retail.xlsx` contains 541,909 invoice-line rows and eight
fields, dated 2010-12-01 through 2011-12-09. The initial inspection found
25,900 invoices, 4,070 stock codes, 38 countries, 135,080 rows with missing
`CustomerID`, 10,624 negative-quantity rows, 2,515 zero-price rows, and two
negative-price rows. These are observed data characteristics, not standalone
reasons to exclude a row.

## Repository map

- `notebooks/01_data_understanding.ipynb` — raw-data profile and transaction
  anomaly investigation; preserves the raw frame.
- `notebooks/02_cleaning.ipynb` — current consolidated analysis: product
  rankings and sensitivity, clean-row waterfall, exact cancellation matching,
  and unmatched-cancellation diagnostics.
- `notebooks/archive/` — earlier product-analysis, cleaning-foundation, and
  partial-return notebooks retained for history, not the current run order.
- `src/clean.py` — reusable stock-code normalization, cancellation matcher,
  and clean-data loader.
- `data/raw/Online Retail.xlsx` — source workbook.
- `requirements.txt` — pinned Python environment dependencies.
- `readme.md` — project overview and setup.

The latest reorganization commit replaced the previous numbered analysis
notebooks with `02_cleaning.ipynb` and moved those predecessors to `archive/`.
Run the current notebooks in order: `01_data_understanding.ipynb`, then
`02_cleaning.ipynb`.

## Work completed and verified findings

### Raw-data and ranking investigation

- The initial notebook profiles transaction types and missing values without
  filtering or overwriting the raw frame. Invoice-line count, invoice count,
  and item quantity are distinct measures.
- In the raw positive-quantity, positive-price ranking, StockCode `23843` has
  an 80,995-unit line with an equal cancellation for the same customer.
  StockCode `23166` has 78,033 positive-price units, of which one line is
  74,215 units (95.1%) and has an exact earlier-sale/cancellation match.
- Ranking results change materially when the largest line is removed or signed
  quantities are netted. These are population-sensitive recorded-quantity
  summaries, not evidence that the underlying transactions were erroneous.
- StockCode `84347` has a -9,360 return shortly after the file begins. Ten
  positive lines for that product occur in the file, but none is an earlier
  purchase for the cancellation's customer. An earlier purchase may predate
  the file; that explanation is plausible, not proven.

### Cleaning and cancellation diagnostics

The current clean-row waterfall applies these four filters in order:

1. Exclude invoices whose number starts with `C`.
2. Keep `Quantity > 0` and `UnitPrice > 0`.
3. Keep product-like stock codes matching five digits plus optional letters.
4. Remove positive lines matched to an earlier cancellation for the same
   customer, stock code, and exact quantity.

The waterfall is **541,909 → 532,621 → 530,104 → 527,725 → 524,894 rows**.
The clean population contains 3,786 products and 5,351,288 positive units.
Rows with missing `CustomerID` are retained in the clean population; they
cannot participate in customer-based cancellation matching. The matcher
diagnostics separately report 383 `C`-invoice cancellation rows with missing
`CustomerID`; these are outside the 8,905 cancellations considered.

`src/clean.py` strips and uppercases stock codes in `load_raw()`. The matcher
uses only eligible product-code lines and cancellations with a `C` prefix,
negative quantity, positive price, and present customer ID. It matches each
cancellation to at most one unused, strictly earlier positive line with the
same customer, normalized stock code, and exact absolute quantity, choosing
the closest earlier candidate. Only matched positive lines are removed;
unmatched and partial-return candidates are not netted. Added `line_value`
means quantity multiplied by unit price (recorded value, not verified
revenue), and `week` is the invoice week start.

Of 8,905 cancellation lines considered, 2,831 matched and 6,074 did not.
The unmatched screen groups these into:

- 4,572 with a larger earlier eligible purchase (23,914 cancellation units);
  these are possible partial-return candidates, not confirmed links.
- 21 with an equal-quantity earlier line that had already been used by another
  cancellation.
- 84 with only smaller earlier eligible purchases.
- 1,031 with no earlier eligible same-customer, same-product purchase in the
  file and a product-like stock code.
- 366 with no earlier purchase in the file and a non-product stock code.

The 1,031 group is concentrated near the beginning of the file: 544 occur in
December 2010 and January 2011 (about 53% of that group), versus 1,068 of all
6,074 unmatched cancellations (about 18%) in those months. This pattern is
consistent with some returns referring to pre-file sales, but does not prove
that explanation.

The 23,914 candidate units are about **0.45% of the 5,351,288 clean units**;
this is a scale comparison, not a verified return rate. The 1,031
no-earlier-purchase cancellations total 18,053 returned units, about 0.34% of
the 5,351,288 clean units, and some may refer to purchases before the file
begins.
The 1,031 lines without an earlier purchase in the file may include returns
whose sales occurred before the file begins. Absence of an earlier in-file
purchase does not establish that no purchase occurred.

## Decisions and rationale

- Gross product rankings use rows with positive quantity and positive unit
  price. They describe recorded positive quantities, not verified demand.
- Signed net quantity is reported separately and includes only rows with
  positive unit price; do not mix it with gross rankings.
- Remove a positive line only on a one-to-one, earlier, exact-quantity match
  for the same identified customer and normalized stock code. Do not remove
  products based on unusual-volume or return-rate thresholds.
- Keep positive rows with missing customer IDs. Do not impute customer
  identity or imply that they were matchable to returns.
- Treat larger-earlier-line cases as candidates only. Do not net partial
  returns or claim the matching algorithm proves the true business event.
- Treat `line_value` as a derived recorded amount, not verified revenue.

## Current status and next steps

Raw-data inspection, product-ranking sensitivity, cleaning, exact matching,
and unmatched-return diagnostics are complete. A within-product price/quantity
analysis has **not** yet been completed. Next, inspect whether product prices
persist over time versus appearing as isolated, bulk, or special-price lines.
Then define comparable product-level observations and assess price/quantity
patterns separately for rows with and without `CustomerID`, with appropriate
time and customer-composition caveats. Keep any observed association
descriptive; do not claim a causal price effect.

## Continuation conventions

- Check which population and unit each reported number uses; distinguish rows,
  invoices, products, lines, and units.
- Preserve the raw workbook/frame. Make cleaning choices explicit and validate
  counts with assertions or an independent calculation.
- Separate direct observations from interpretations and state uncertainty,
  especially for cancellation linkage and the file-start boundary.
- Use the shared helpers in `src/clean.py` rather than duplicating the matcher.
- Keep changes scoped to requested files, review `git diff`, and stage explicit
  paths rather than using `git add .`.
