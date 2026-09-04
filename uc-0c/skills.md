skills:
  - name: load_dataset
    description: Ingests the municipal ward budget CSV, validates required schema headers, and audits all data rows to detect and register missing or null actual_spend values.
    input: input_path (str) to the source budget CSV file.
    output: Tuple or structured object containing the parsed rows, total row count, list of validated wards and categories, and an audit list of all detected null rows with notes.
    error_handling: Raises descriptive errors if the file is missing, headers do not match expected schema, or file is unreadable.

  - name: compute_growth
    description: Computes period-over-period expenditure growth (MoM or YoY) for a specific ward and category, generating explicit calculation formulas and flagging any null periods.
    input: dataset (list of dicts), ward (str), category (str), growth_type (str - 'MoM' or 'YoY').
    output: List of structured per-period dictionaries containing period, ward, category, budgeted_amount, actual_spend, growth_type, growth_rate, formula, status, notes.
    error_handling: Refuses execution if ward or category is not found, if growth_type is missing/invalid, or if global multi-ward aggregation is requested.
