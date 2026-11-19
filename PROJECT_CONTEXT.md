# Project context

## Objective and interpretation

Describe how observed weekly modal prices relate to recorded invoices and
units for comparable products in the UCI Online Retail data. This is an
observational analysis, not a causal estimate of demand. Recorded quantities
are not verified demand or necessarily completed sales. Interpret the
estimates as association, not causal; recorded quantity is not verified
demand.

## Canonical notebook order

Run from the repository root, top to bottom:

1. `notebooks/01_data_understanding.ipynb` — raw-data profile, transaction
   classes, and anomaly investigation; the raw frame is preserved.
2. `notebooks/02_cleaning.ipynb` — ranking sensitivity, clean-row waterfall,
   exact cancellation matching, and unmatched-cancellation screening.
3. `notebooks/03_price_variation.ipynb` — product-week construction, mixed
   prices, modal-price deviations, persistence, and descriptive correlations.
4. `notebooks/04_elasticity.ipynb` — model samples, Sample B specifications,
   robustness checks, broad Sample E within-product models, and price-range
   terciles.
5. `notebooks/05_price_tiers.ipynb` — price-ratio summaries and within-product
   estimates by CustomerID status.

`notebooks/archive/` holds superseded notebooks; do not include them in the
current run sequence.

## Repository map

- `data/raw/Online Retail.xlsx` — source workbook.
- `notebooks/01_data_understanding.ipynb` through
  `notebooks/05_price_tiers.ipynb` — current analysis sequence.
- `notebooks/archive/` — historical notebooks.
- `src/clean.py` — `load_raw`, `load_clean`, `normalize_stock_codes`, and
  `match_cancelled_orders`.
- `src/features.py` — `build_product_week`.
- `src/models.py` — `fit_within_product`.
- `requirements.txt` — Python dependencies.
- `readme.md` — project overview, workflow, and key results.

## Data profile and cleaning decisions

The raw workbook has 541,909 invoice-line rows and eight fields, dated
2010-12-01 through 2011-12-09. Notebook 01 reports 25,900 invoices, 4,070
stock codes, 4,372 non-missing customer IDs, 38 countries, and 135,080 rows
with missing `CustomerID`. It also reports 10,624 negative-quantity rows,
2,515 zero-price rows, and two negative-price rows. These are observed data
characteristics, not standalone cleaning rules.

Notebook 02 applies these filters in order:

1. Exclude invoices whose number starts with `C`.
2. Keep `Quantity > 0` and `UnitPrice > 0`.
3. Keep stock codes matching five digits plus optional letters.
4. Remove only positive lines matched one-to-one to a strictly earlier
   cancellation for the same identified customer, stock code, and exact
   quantity. A positive line can be used once; the closest earlier match is
   selected.
5. Retain positive lines with missing `CustomerID`; they cannot participate
   in customer-based matching.

The printed row waterfall is **541,909 → 532,621 → 530,104 → 527,725 →
524,894**. The final clean population has 3,786 products and 5,351,288 units.
The clean loader also adds `line_value` and invoice-week `week`.

The cancellation matcher considered 8,905 lines: 2,831 matched and 6,074
unmatched. The unmatched screen reports 4,572 larger-earlier-purchase
candidates with 23,914 cancellation units, 21 with an equal earlier line
already used, 84 with only smaller earlier purchases, 1,031 with no earlier
eligible same-customer/same-product purchase in the file and a product-like
code, and 366 with no earlier purchase and a non-product code. These are
candidate groupings, not proof of return linkage. The notebook reports 544 of
the 1,031 product-like no-earlier-purchase cases in December 2010 and January
2011 (about 53%); pre-file purchases are a possibility, not a conclusion.

## Completed analysis and notebook results

### Product-week price variation

Notebook 03 builds 100,068 product-weeks from the clean rows. It reports
46,112 mixed-price product-weeks (46.08%), containing 4,267,571 units. Among
these, the lowest-price median line quantity is larger in 38,453 cases
(83.39%). For products active at least 10 weeks, 2,004 meet the notebook's
5% price-deviation and activity criteria; 960 have a run of at least three
consecutive deviating calendar weeks, 489 have only isolated single-week
deviations, and 555 have a longest run of exactly two.

The notebook also reports median per-product Spearman correlations. For all
product-weeks, the medians are -0.390 for units, -0.141 for invoices, and
-0.433 for median line quantity. For single-price product-weeks, they are
-0.505, -0.194, and -0.482, respectively. These are distributions of
within-product correlations, not pooled causal effects.

### Final model choice and within-product results

Notebook 04's Section 1 filtered modeling base contains 38,653 product-weeks
across 1,913 products and 641,536 units. This is not the same population as
broad Sample E. Section 6's eligible Sample E contains 83,377 observations
across 2,523 products; eligible Sample B contains 5,533 observations across
348 products.

`fit_within_product` demeans outcomes and regressors by `StockCode`, includes
week effects, and clusters standard errors by `StockCode`. The saved notebook
outputs select within-product OLS with week effects on Sample E. The headline
`log_invoices` coefficient is -0.397409 (clustered SE 0.014191). Across
invoice models in Sections 5-8, the coefficient range is -0.493071 to
-0.311295; the lower endpoint is the Section 8 restricted-E estimate
(`mode_share_units >= 0.9`), and the upper endpoint is Section 6's
`E-invoices-mode-share` estimate.

| Sample/specification | Outcome | `log_price` coefficient | Clustered SE | Observations | Products |
|---|---|---:|---:|---:|---:|
| E, no extra control | `log_invoices` | -0.397409 | 0.014191 | 83,377 | 2,523 |
| E, no extra control | `log_units` | -1.502479 | 0.024650 | 83,377 | 2,523 |
| E, controlling for `mode_share_lines` | `log_invoices` | -0.311295 | 0.013345 | 83,377 | 2,523 |
| B, no extra control | `log_invoices` | -0.332338 | 0.044845 | 5,533 | 348 |
| E, `mode_share_units >= 0.9` | `log_invoices` | -0.493071 | 0.016006 | 56,298 | 2,518 |

The Sample B decomposition reports `log_invoices` at -0.332338 (clustered SE
0.044845) and `log_units_per_invoice` at -1.165481 (0.048999). The latter
association is larger in magnitude, indicating that the units relationship
in this decomposition is more associated with order size than invoice count;
the two coefficients sum to the Sample B `log_units` coefficient of -1.497819.

### CustomerID price patterns and sensitivity

Notebook 05 reports 517,559 qualifying lines: 128,801 with missing
CustomerID and 388,758 with an identified CustomerID. In every quantity
bucket, the identified group's median price ratio is 1.000; the missing-ID
group's bucket medians range from 1.920 to 2.000. This is evidence of distinct
price patterns, but the distributions are not proof of non-overlapping tiers.
The idea that missing CustomerID identifies a retail tier is a hypothesis.

Within-product estimates by CustomerID status are:

| Group | Outcome | `log_price` coefficient | Clustered SE | 95% CI | Observations | Products |
|---|---|---:|---:|---:|---:|---:|
| All | `log_invoices` | -0.397409 | 0.014191 | [-0.425223, -0.369594] | 83,377 | 2,523 |
| All | `log_units` | -1.502479 | 0.024650 | [-1.550792, -1.454167] | 83,377 | 2,523 |
| Identified | `log_invoices` | -0.493074 | 0.024273 | [-0.540648, -0.445500] | 50,237 | 1,597 |
| Identified | `log_units` | -1.703228 | 0.040197 | [-1.782013, -1.624443] | 50,237 | 1,597 |
| Missing | `log_invoices` | -0.494630 | 0.022055 | [-0.537857, -0.451403] | 45,449 | 1,851 |
| Missing | `log_units` | -1.324769 | 0.032200 | [-1.387880, -1.261657] | 45,449 | 1,851 |

Both customer groups have negative `log_invoices` coefficients that are not
near zero, supporting the negative association in the main model under this
split. This is a sensitivity check, not a causal result or a reason to change
the main model.

## Limitations and open work

- Product-weeks with no recorded transactions are absent; zero-sales weeks
  are not imputed.
- Weekly modal price can conceal transaction-level prices, discounts, and
  the distinct price patterns associated with identified and missing
  CustomerID lines.
- The workbook does not include stock availability, unmet demand, or cost
  data.
- Recorded quantity is not verified demand.
- The observed period is limited to the workbook's dates; longer histories
  could test persistence.
- Price, seasonality, bulk purchasing, promotions, and customer composition
  can move together. The estimates are association, not causal.
- If causal inference is pursued, obtain suitable availability/transaction
  data and specify an identification strategy before interpreting a price
  effect.

## Continuation conventions

- Keep the distinction between rows, invoices, products, product-weeks, and
  units; report the population attached to every count.
- Preserve the raw workbook and keep data rules explicit and testable.
- Use `src.clean`, `src.features`, and `src.models` instead of duplicating
  shared transformations.
- Treat unmatched and partial-return cases as candidates, not confirmed
  cancellation links.
- Review the focused diff, preserve unrelated worktree changes, and do not
  commit unless explicitly requested.
