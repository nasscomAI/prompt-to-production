skills:
  - name: load_dataset
    description: Reads ward_budget.csv, validates required columns, and prints a null report before returning filtered data.
    input: file_path (str), ward (str), category (str)
    output: list of dicts for the matching ward+category rows only, sorted by period; prints null count and which rows are null before returning
    error_handling: if ward or category not found in dataset, raise ValueError with the exact value that failed; if required columns missing, raise ValueError listing missing columns

  - name: compute_growth
    description: Takes filtered rows and computes MoM or YoY growth per period, showing formula for every row.
    input: rows (list of dicts from load_dataset), growth_type (str: "MoM" or "YoY")
    output: list of dicts with period, actual_spend, growth_pct, formula, null_flag — null rows included with null_flag=NULL and growth_pct=N/A
    error_handling: if growth_type is not MoM or YoY, raise ValueError; if a row has null actual_spend, include it with null_flag=NULL and skip growth computation for that period only