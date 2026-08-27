# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Reads the ward_budget CSV, validates required columns exist, and reports null actual_spend rows with their reasons before returning the data.
    input: >
      file_path (str) — path to the ward_budget.csv file.
    output: >
      A list of row dictionaries with all CSV columns preserved.
      A printed report listing: total rows, unique wards, unique categories,
      null actual_spend count, and for each null row: period, ward, category, and notes reason.
    error_handling: >
      If required columns (period, ward, category, budgeted_amount, actual_spend, notes) are missing,
      raises ValueError listing the missing columns.
      If file does not exist, raises FileNotFoundError.

  - name: compute_growth
    description: Takes a ward, category, and growth_type, filters the dataset, and returns a per-period growth table with the formula shown for each row.
    input: >
      data (list[dict]) — full dataset from load_dataset.
      ward (str) — exact ward name to filter on.
      category (str) — exact category name to filter on.
      growth_type (str) — "MoM" (month-over-month). Must be explicitly provided.
    output: >
      A list of dictionaries, one per period, with keys: period, ward, category,
      actual_spend, growth_pct (str — formatted percentage or NULL flag),
      formula (str — the calculation shown), flag (str — null/error flags or empty).
    error_handling: >
      If ward or category not found in data, raises ValueError listing available values.
      If growth_type is not provided or not recognized, refuses and lists valid options.
      Null actual_spend rows produce growth_pct="NULL" with flag containing the notes reason.
      The period after a null flags that its predecessor was null.
