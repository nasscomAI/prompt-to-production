skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates required columns, detects deliberate null rows in actual_spend, and logs null counts and row details before processing.
    input: file_path (str path to ward_budget.csv)
    output: list of validated budget records (dicts)
    error_handling: Raises ValueError if required columns are missing; flags and isolates null rows with note explanations.

  - name: compute_growth
    description: Computes period-over-period (MoM / YoY) growth for a single ward and single category, formats percentage changes, shows formulas, and flags uncomputable null rows.
    input: records (list of dicts), ward (str), category (str), growth_type (str: 'MoM' or 'YoY')
    output: list of dicts representing the growth output table
    error_handling: Refuses calculation if growth_type is missing or if ward/category filters are not provided; marks missing period data as NOT_COMPUTED with reason.
