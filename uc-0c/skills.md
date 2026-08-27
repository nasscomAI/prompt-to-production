# skills.md — UC-0C Budget Growth Calculator

skills:
  - name: load_dataset
    description: Reads CSV budget data, validates required columns exist, and reports null count and specific rows with null actual_spend before returning data.
    input: String file path to CSV with columns (period, ward, category, budgeted_amount, actual_spend, notes).
    output: Returns pandas DataFrame with all rows, and prints to stdout the total null count and list of rows with null actual_spend (showing period, ward, category, and notes). Raises ValueError if required columns missing.
    error_handling: If file not found, raises FileNotFoundError with clear message. If required columns (period, ward, category, actual_spend) are missing, raises ValueError listing missing columns. If CSV is malformed, raises pandas parsing error with row number.

  - name: compute_growth
    description: Computes period-over-period growth rates for a specific ward-category combination, showing formula for each period and flagging null values.
    input: DataFrame from load_dataset, string ward name, string category name, string growth_type ('MoM' or 'YoY').
    output: Returns DataFrame with columns (period, actual_spend, growth_rate, formula, flag) for the specified ward-category only. Null actual_spend rows have growth_rate='NULL', formula='N/A', flag with reason from notes. First period has growth_rate='N/A', formula='No prior period'. All computed rows show formula like '(19.7 - 14.8) / 14.8 = 33.1%'.
    error_handling: If ward not found in data, raises ValueError listing available wards. If category not found for that ward, raises ValueError listing available categories. If growth_type not 'MoM' or 'YoY', raises ValueError requesting valid type. If no rows match ward-category filter, raises ValueError indicating no data found.
