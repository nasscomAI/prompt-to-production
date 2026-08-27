# skills.md

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates all required columns, reports null count and which rows have missing actual_spend values before returning data.
    input: "Path to budget CSV file (ward_budget.csv)"
    output: "Dictionary with keys: data (pandas DataFrame), null_rows (list of dicts with period/ward/category/reason/notes), total_nulls (int). Example: {\"data\": <DataFrame>, \"null_rows\": [{\"period\": \"2024-03\", \"ward\": \"Ward 2\", \"category\": \"Drainage\", \"reason\": \"[reason from notes]\"}], \"total_nulls\": 5}"
    error_handling: "If file not found, raise error. If required columns missing (period, ward, category, budgeted_amount, actual_spend, notes), raise error. Count and log all null rows before returning. If actual_spend cannot be parsed as float where not null, log warning with row."

  - name: compute_growth
    description: Takes ward, category, growth_type (MoM or YoY), and computes per-period growth from the dataset, returning table with actual spend, formula, and growth percentage.
    input: "DataFrame from load_dataset, ward (string), category (string), growth_type ('MoM' or 'YoY')"
    output: "CSV file with columns: period, actual_spend, previous_period_spend, formula, growth_percent. Example row: '2024-07,19.7,14.8,(19.7-14.8)/14.8*100,+33.1%'. Null rows shown as 'NULL — [reason]'."
    error_handling: "If ward not in data, raise error. If category not in data, raise error. If growth_type not 'MoM' or 'YoY', raise error. If request implies cross-ward or cross-category aggregation, refuse with explicit message. For null actual_spend, show NULL with reason from notes column, do not compute. If no valid non-null values for period comparison, return empty result with explanation."
