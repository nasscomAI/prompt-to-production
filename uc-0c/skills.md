# skills.md

skills:
  - name: load_dataset
    description: Load CSV budget data, validate required columns, identify and report all null rows before returning data.
    input: "CSV filepath (string); validates 6 required columns: period, ward, category, budgeted_amount, actual_spend, notes"
    output: "DataFrame with data + List of null rows (each with period, ward, category, notes); total null count reported"
    error_handling: "If file not found, raise FileNotFoundError. If required columns missing, raise ValueError listing missing columns"

  - name: validate_parameters
    description: Verify that requested ward and category exist in dataset; refuse with valid options if not found.
    input: "DataFrame, ward (string), category (string), growth_type (string); checks against unique values in dataset"
    output: "OK (validation passes) or ERROR with list of valid wards/categories; checks growth_type is 'MoM' or 'YoY'"
    error_handling: "If ward not found, return ERROR listing all valid wards. If category not found, return ERROR listing all valid categories. If growth_type invalid, raise ValueError"

  - name: compute_growth
    description: Calculate Month-over-Month or Year-over-Year growth for a specific ward & category. Shows formula in every row.
    input: "DataFrame, ward (string), category (string), growth_type ('MoM' or 'YoY'); filters to specific ward+category pair only"
    output: "DataFrame with columns [period, actual_spend, growth_percent, formula, null_reason, is_null]; formula shown for every row"
    error_handling: "If no data for ward+category pair, raise ValueError. If prior period/year is null, set growth_percent to None and formula to 'N/A - Prior period NULL'. For first month (MoM), growth is None with formula 'N/A - First Month'"

  - name: generate_report
    description: Create human-readable report showing filter parameters, null row flags, and growth calculation summary.
    input: "DataFrame, null_rows list, ward (string), category (string), growth_type (string)"
    output: "Multi-line string report with: filter parameters, total nulls count, flagged null rows with reasons, growth calculation table"
    error_handling: "If null_rows empty, still generate report but show 'No null rows'. Always show growth calculation parameters clearly"
