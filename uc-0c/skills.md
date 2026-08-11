# skills.md — UC-0C Budget Growth Calculator

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates the required columns, and reports every null row with its notes reason before any computation.
    input: input_path (string) to ward_budget.csv.
    output: list of rows (dicts) plus a printed null report (period, ward, category, notes for each null row).
    error_handling: Missing file or missing columns raises a clear error; null actual_spend rows are reported, never silently dropped.

  - name: compute_growth
    description: Computes per-period growth for exactly one ward + category with the requested growth type and writes the per-ward per-category table.
    input: rows, ward (string), category (string), growth_type (MoM).
    output: CSV with columns period, ward, category, budgeted_amount, actual_spend, previous_actual_spend, growth_percent, formula, flag.
    error_handling: Refuses ward/category = ALL or an unspecified growth type; rows with null actual_spend get growth_percent NA and flag = NULL_FLAG with the notes reason.
