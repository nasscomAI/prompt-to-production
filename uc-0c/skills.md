skills:
  - name: load_dataset
    description: Reads the input CSV file, validates schema and column types, and reports total rows, null counts, and specific null row details prior to calculation.
    input: File path to ward budget CSV (input_path).
    output: Tuple containing loaded dataset records (list of dicts) and a null report summary (dict/list of null rows).
    error_handling: Flags missing columns, invalid data types, or empty files; raises descriptive errors and details null locations.

  - name: compute_growth
    description: Takes filtered ward, category, and growth_type parameters to produce a period-by-period growth table including formula descriptions and null handling flags.
    input: Filtered dataset records, ward string, category string, and growth_type string.
    output: Table data (list of dicts) containing period, ward, category, actual_spend, mom_growth_percent, formula, and flag_notes.
    error_handling: Refuses execution if ward, category, or growth_type is missing/invalid; skips calculation on NULL spend rows and reports note reasons.
