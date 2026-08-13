skills:
  - name: load_dataset
    description: Reads ward_budget.csv, validates schema and column types, scans for null actual_spend rows, and prints an explicit null audit report with row notes before returning data.
    input: input_path (str) - path to budget CSV file
    output: tuple of (list of data dicts, list of flagged null row dicts)
    error_handling: Raises FileNotFoundError if CSV missing, or ValueError if required columns absent.

  - name: compute_growth
    description: Computes per-period growth (MoM/YoY) for a specific ward and category, refusing cross-ward aggregations or missing growth types, and appending formula strings to output.
    input: dataset (list), ward (str), category (str), growth_type (str)
    output: list of dicts with keys (period, ward, category, budgeted_amount, actual_spend, growth_pct, formula, notes)
    error_handling: Raises ValueError if aggregation across wards requested or growth_type omitted.

