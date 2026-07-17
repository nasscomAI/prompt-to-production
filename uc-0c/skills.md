skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates its columns, and reports the null count and specific null rows before returning the data.
    input: File path (string) to a CSV, e.g. ../data/budget/ward_budget.csv, with expected columns period, ward, category, budgeted_amount, actual_spend, notes.
    output: Validated in-memory dataset (e.g. dataframe/list of records) plus a null report listing count of null actual_spend rows and their period, ward, category, and notes reason.
    error_handling: >
      If required columns are missing or malformed, refuses to load and reports which
      columns are invalid. If actual_spend nulls are present, does not silently drop or
      fill them — flags each null row with its notes reason before returning the dataset.
      If the file cannot be found or read, refuses and reports the file path issue rather
      than proceeding with partial or assumed data.

  - name: compute_growth
    description: Takes a ward, category, and growth_type, and returns a per-period growth table with the formula shown for each row.
    input: Ward (string), category (string), and growth_type (string, must be "MoM" or "YoY"), plus the validated dataset from load_dataset.
    output: Per-period table (rows = periods for the given ward and category) where each row shows period, actual_spend, growth value, and the exact formula used to compute it.
    error_handling: >
      If growth_type is not specified, refuses to guess and asks the user to specify MoM
      or YoY. If ward or category is missing, ambiguous, or matches multiple entries,
      refuses and asks for clarification rather than aggregating across wards or
      categories. If a period's actual_spend is null, does not compute a growth value for
      that row — flags it as null with the reason from notes instead. Never returns a
      single aggregated number across wards or categories; always returns the per-ward
      per-category table.