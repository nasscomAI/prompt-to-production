# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.
skills:
  - name: load_dataset
    description: Reads the budget CSV, validates expected columns, and reports null count and which specific rows are null before returning data.
    input: file path (str) to ward_budget.csv.
    output: A list of row dicts (period, ward, category, budgeted_amount, actual_spend, notes), plus a printed/logged report of null rows found.
    error_handling: If expected columns are missing, raise a clear error naming which column is missing rather than failing silently downstream.

  - name: compute_growth
    description: Computes MoM or YoY growth for one ward+category pair across all periods, showing the formula used per row.
    input: dataset (from load_dataset), ward (str), category (str), growth_type ("MoM" or "YoY").
    output: A list of dicts, one per period, each with period, actual_spend, growth_pct (or a null flag), formula_used.
    error_handling: If growth_type is missing or invalid, refuse and return an error message asking the user to specify MoM or YoY. If a period's actual_spend is null, output growth_pct as "NULL - FLAGGED" with the reason from notes, not a computed number.