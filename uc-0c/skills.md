# skills.md

skills:

- name: load_dataset
  description: Reads CSV, validates structure, reports null count and identifies which rows contain missing actual_spend values.
  input: File path (string) to ward_budget.csv
  output: Parsed DataFrame with 300 rows, all 5 columns present; null rows flagged with row index and notes reason before returning
  error_handling: Refuse if file not found; validate required columns (period, ward, category, budgeted_amount, actual_spend, notes) exist; explicitly report which 5 rows are null and their reasons.

- name: compute_growth
  description: Computes per-period MoM or YoY growth for a specified ward + category combination, showing formula used in every row.
  input: Loaded dataset, ward (string), category (string), growth_type (enum: "MoM" or "YoY")
  output: Per-period time-series table with columns: period, actual_spend (₹ lakh), growth_percentage, formula; null rows in selection must be flagged with reason before computing
  error_handling: Refuse if ward or category not specified; refuse if growth_type not specified or invalid; refuse if ward/category combination not found in dataset; flag null rows _before_ computing growth; do not aggregate across wards or categories.
