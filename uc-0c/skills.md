# skills.md
# UC-0C Skills

skills:
  - name: load_dataset
    description: Reads CSV file, validates column structure, identifies and reports all rows with null actual_spend before returning DataFrame.
    input: |
      filepath (string): Path to ward_budget.csv
      Example: "../data/budget/ward_budget.csv"
    output: |
      (DataFrame, null_info_dict)
      DataFrame: All 300 rows with columns [period, ward, category, budgeted_amount, actual_spend, notes]
      null_info_dict: {
        'count': integer (number of null rows),
        'rows': list of dicts [{'period': YYYY-MM, 'ward': string, 'category': string, 'notes': string}]
      }
    error_handling: |
      - FileNotFoundError if file does not exist → raise with explicit path
      - ValueError if columns missing (raises immediately with list of missing columns)
      - ValueError if file not valid CSV → raise with parse error details
      - Before returning, scans entire DataFrame for actual_spend = null or empty and includes in null_info
      - Never silently ignores nulls; caller must be informed of all 5 null rows

  - name: validate_parameters
    description: Checks that ward name, category name, and growth_type are valid and required. Enforces refusal if growth_type not specified.
    input: |
      (DataFrame, ward_name, category_name, growth_type)
      - DataFrame: loaded dataset
      - ward_name: string (e.g., "Ward 1 – Kasba")
      - category_name: string (e.g., "Roads & Pothole Repair")
      - growth_type: string or None (must be "MoM" or "YoY")
    output: |
      None (on success)
    error_handling: |
      - If growth_type is None → raise ValueError with message: "REFUSAL: --growth-type must be specified (MoM or YoY)"
      - If growth_type not in ['MoM', 'YoY'] → raise ValueError with message: "REFUSAL: --growth-type must be MoM or YoY"
      - If ward_name not in DataFrame wards → raise ValueError listing all valid wards
      - If category_name not in DataFrame categories → raise ValueError listing all valid categories
      - No defaults, no guessing — always refuse ambiguity explicitly

  - name: compute_growth
    description: For a single ward and category, computes month-over-month or year-over-year growth, returns time-ordered table with formulas shown for every row.
    input: |
      (DataFrame, ward_name, category_name, growth_type)
      - DataFrame: loaded dataset (pre-filtered calls this on full dataset)
      - ward_name: validated ward string
      - category_name: validated category string
      - growth_type: validated string ("MoM" or "YoY")
    output: |
      DataFrame with columns:
      - period: YYYY-MM format, sorted ascending
      - actual_spend: float (₹ lakh) or NaN if null
      - growth_value: float (difference from prior) or NaN if cannot compute
      - growth_pct: float (% change, 1 decimal) or NaN if cannot compute
      - formula: string showing exact calculation or reason (e.g., "First record — no prior data")
      - status: string ("OK", "NULL_FLAGGED", "CANNOT_COMPUTE")
    error_handling: |
      - If no data found for ward+category combination → raise ValueError
      - For null actual_spend in current month → status=NULL_FLAGGED, formula="N/A — actual_spend is null"
      - For first month of series → no prior data, formula="First record — no prior data"
      - For MoM: if previous month is null → status=CANNOT_COMPUTE, formula="MoM: previous month (YYYY-MM) is NULL"
      - For MoM: if previous month does not exist → status=CANNOT_COMPUTE (should not happen in 12-month series)
      - For YoY: if previous year same month not in data → status=CANNOT_COMPUTE, formula="YoY: no data for YYYY-MM"
      - For YoY: if previous year same month is null → status=CANNOT_COMPUTE, formula="YoY: YYYY-MM is NULL"
      - Never skip rows; all 12 months included in output (some with null or CANNOT_COMPUTE status)

  - name: generate_output_csv
    description: Writes growth computation results to CSV file with proper formatting.
    input: |
      (result_dataframe, output_filepath)
      - result_dataframe: DataFrame returned from compute_growth (12 rows)
      - output_filepath: string path for output file (e.g., "growth_output.csv")
    output: |
      File written to disk; no return value
    error_handling: |
      - IOError if output directory does not exist → create directory or raise explicit error
      - If write fails → raise with file path and system error details
      - Ensures CSV is readable and preserves formula strings (may need escaping for commas)
