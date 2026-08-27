skills:
  - name: load_dataset
    description: >
      Reads ward_budget.csv, validates expected columns
      (period, ward, category, budgeted_amount, actual_spend, notes),
      reports count of null actual_spend rows and lists them before returning.
      Uses the --input argument to locate the file.
    input: >
      CLI arguments: --input <path>, defaults to
      ../data/budget/ward_budget.csv
    output: Parsed dataset as a list of rows, with null rows enumerated
    error_handling: >
      If the file is missing, required columns are absent, or the CSV is malformed,
      raise a clear error and halt — do not proceed to compute growth on incomplete data.

  - name: compute_growth
    description: >
      Computes per-period growth (MoM or YoY) for a specific ward and category,
      returning a per-ward, per-category table that includes the formula used
      and flags any null rows with the reason from the notes column.
      Never aggregates across wards or categories — refuse any request for
      an all-wards or all-categories aggregate.
    input: >
      CLI arguments: --ward <name>, --category <name>, --growth-type MoM|YoY,
      parsed dataset from load_dataset.
      If --growth-type is omitted, refuse — do not guess.
    output: >
      CSV with one row per (ward, category, period) containing columns:
      (ward, category, period, actual_spend, growth_value, formula, null_flag, null_reason)
    error_handling: >
      If growth_type is not provided, refuse and ask the user to specify MoM or YoY explicitly.
      If ward or category does not exist in the dataset, return an empty result with an explanation.
      If actual_spend is null, set growth_value to NULL and populate null_reason from the notes column.
