# Pricing and recorded quantity

## Project question

How does price relate to recorded quantity for comparable products? This
project is exploratory: recorded quantity is not the same as customer demand,
and an association between price and quantity does not establish causation.

## Data

The source is the UCI Online Retail dataset, covering 2010-12-01 to 2011-12-09.
Place the workbook at `data/raw/Online Retail.xlsx`.

## Repository structure

- `data/raw/` — source workbook
- `notebooks/` — inspection, cleaning, and product analysis
- `src/clean.py` — reusable cleaning and cancellation-matching logic
- `PROJECT_CONTEXT.md` — project decisions, findings, and open questions

## How to run

1. Create `.venv` if needed, then activate it in PowerShell with
   `.\.venv\Scripts\Activate.ps1`.
2. Open the notebooks in Jupyter or VS Code.
3. Restart the kernel and run all cells in order: `01_data_understanding`,
   `03_clean_foundation`, then `02_product_analysis`.

Install the packages listed in `requirements.txt` when setting up the
environment.

## Current status and limitations

The project has raw-data inspection, a reproducible cleaning foundation, and
initial product rankings. Cancellation matching removes an original positive
line only when an earlier line matches customer, stock code, and exact quantity.
The rules are provisional and unmatched cancellations are not linked to sales.

Recorded quantity is not verified demand or completed sales. Price and quantity
may reflect returns, timing, customer mix, and other factors. Any observed
association is descriptive, not causal; product comparisons need further work.