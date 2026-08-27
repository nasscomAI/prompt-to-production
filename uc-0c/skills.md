skills:
  - name: load_dataset
    description: Reads the budget CSV, validates required columns, parses numeric values, and reports null actual_spend rows with context.
    input: A string path to the input CSV file.
    output: A list of row dictionaries with parsed values and an added `period_date` field for sorting.
    error_handling: Raises an error for missing files, invalid headers, malformed period values, or non-numeric amounts.

  - name: compute_growth
    description: Computes period-over-period growth for one ward and one category, flags null values, and includes formula details.
    input: A ward string, a category string, a growth type string, and the loaded dataset rows.
    output: A list of output dictionaries containing `period`, `ward`, `category`, `actual_spend`, `growth_type`, `formula`, `growth_pct`, `status`, and `notes`.
    error_handling: Raises if the ward/category combination is not found, if the growth type is unsupported, or if the prior period data needed for growth is unavailable.
