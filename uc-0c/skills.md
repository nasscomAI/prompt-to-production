# skills.md — UC-0C Budget Growth Calculator

skills:
  - name: load_dataset
    description: Reads ward_budget.csv, separates clean rows from null-spend rows, and returns both lists.
    input: file_path (str) — path to ward_budget.csv.
    output: Tuple (clean_rows, null_rows) where each element is a list of dicts with keys period, ward, category, actual_spend, notes.
    error_handling: Raises FileNotFoundError if path is missing; raises ValueError if CSV is missing required columns (period, ward, category, actual_spend).

  - name: compute_growth
    description: Computes MoM or YoY growth for a single ward+category combination with formula per row.
    input: clean_rows (list of dicts), ward (str exact name with em dash), category (str), growth_type (str 'MoM' or 'YoY').
    output: List of dicts with keys period, actual_spend, growth_pct, formula; ordered chronologically.
    error_handling: Raises ValueError if ward or category is not found in clean_rows; raises ValueError if growth_type is not 'MoM' or 'YoY'; first period row always returns growth_pct='N/A (first period)'.
