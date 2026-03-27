skills:
  - name: load_dataset
    description: Read and validate budget CSV, report null count and locations before returning filtered data.
    input: file path (string) pointing to ward_budget.csv
    output: object with fields {dataframe: DataFrame, null_summary: {count: int, locations: list of {period, ward, category, reason}}}
    error_handling: If file not found, raise IOError. If columns missing (period, ward, category, budgeted_amount, actual_spend, notes), raise ValueError listing missing columns. Before returning, scan for null actual_spend values and report count, locations, and reasons from notes column.

  - name: compute_growth
    description: Calculate MoM or YoY spending growth for specified ward and category, showing formula in output.
    input: object {dataframe: DataFrame, ward: string, category: string, growth_type: string (MoM or YoY)}
    output: DataFrame with columns {period, actual_spend, growth_percent, formula_used, null_flag, null_reason}
    error_handling: If growth_type not MoM or YoY, raise ValueError. If ward not found, raise ValueError. If category not found, raise ValueError. If any row has null actual_spend, set growth_percent to NULL_FLAG and include reason. Never compute growth from null values. If growth cannot be calculated (insufficient prior period data), mark as N/A_FIRST_PERIOD.
