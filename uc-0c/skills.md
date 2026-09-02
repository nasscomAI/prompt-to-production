skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates required columns, and reports the count and identity of null actual_spend rows before any computation happens.
    input: Path to the input CSV file (period, ward, category, budgeted_amount, actual_spend, notes columns expected).
    output: A validated dataset (e.g. list of row dicts) plus a report listing how many rows have null actual_spend and which period/ward/category each null row belongs to, with its notes reason.
    error_handling: If required columns are missing or the file cannot be read, raise a clear error identifying the missing column(s) or file issue rather than proceeding with partial data.

  - name: compute_growth
    description: Computes per-period growth (MoM or YoY) for exactly one ward and category, flagging any period whose actual_spend is null instead of computing it.
    input: The loaded dataset, plus ward (string), category (string), and growth_type (MoM or YoY) — growth_type is required, not optional.
    output: A per-period table with period, actual_spend, growth value, the formula used, and a flag/reason for any period where actual_spend was null.
    error_handling: If ward or category does not match any rows in the dataset, refuse and report that no matching rows were found. If growth_type is missing or not one of MoM/YoY, refuse and ask the user to specify it rather than defaulting to either.