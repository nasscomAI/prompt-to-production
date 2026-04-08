# skills.md — UC-0C Budget Growth Calculation

skills:
  - name: load_dataset
    description: Reads ward budget CSV file, validates required columns exist, and reports null actual_spend values with their count and reasons before returning data.
    input: File path (string) to CSV with columns period, ward, category, budgeted_amount, actual_spend, notes.
    output: Dictionary containing (1) 'data' key with list of row dictionaries, (2) 'null_report' key with dictionary showing null_count (integer) and null_rows (list of dicts with period, ward, category, reason). Returns complete dataset without filtering. Validates all required columns are present.
    error_handling: If file does not exist, raises FileNotFoundError with clear message. If required columns (period, ward, category, budgeted_amount, actual_spend, notes) are missing, raises ValueError listing which columns are absent. If CSV is empty or malformed, raises ValueError with details. Does NOT fail on null actual_spend values—reports them in null_report.

  - name: compute_growth
    description: Filters dataset to specified ward and category, then computes growth (MoM or YoY) for each period with ward and category columns repeated in every row.
    input: Dictionary with keys 'data' (list from load_dataset), 'ward' (string matching exact ward name), 'category' (string matching exact category name), 'growth_type' (string - 'MoM' or 'YoY').
    output: Dictionary containing (1) 'results' key with list of dicts per period showing ward, category, period, actual_spend (₹ lakh), and growth column (named 'mom_growth' or 'yoy_growth' based on type) with values like '+33.1%', '−34.8%', 'NULL - reason', or 'N/A - no prior period', (2) 'metadata' with ward, category, growth_type, total_periods, calculable_periods. Ward and category values repeated in every result row.
    error_handling: If ward or category does not exist in data, raises ValueError listing all valid ward names or category names. If growth_type is not 'MoM' or 'YoY', raises ValueError with message 'growth_type must be MoM or YoY'. If filtered dataset is empty (no rows match ward+category), raises ValueError stating no data found for that combination. For null actual_spend values, shows 'NULL' in spend column and includes reason in growth column. For first period (MoM) or periods without prior year data (YoY), shows actual spend value and 'N/A - no prior period' in growth column.
