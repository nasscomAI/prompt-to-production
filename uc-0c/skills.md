# skills.md — UC-0C Budget Growth Calculator

skills:
  - name: load_dataset
    description: Reads budget CSV file, validates columns, and reports null values with their reasons before returning data.
    input: >
      A file path (string) to a CSV file with columns: period, ward, category,
      budgeted_amount, actual_spend, notes.
    output: >
      A dictionary with keys:
      - data: list of dictionaries (one per row)
      - null_report: list of dictionaries describing each null actual_spend row
        (period, ward, category, reason from notes)
      - wards: list of unique ward names
      - categories: list of unique category names
      - periods: list of unique periods in sorted order
    error_handling: >
      If file doesn't exist: raise FileNotFoundError.
      If required columns missing: raise ValueError with list of missing columns.
      Always report null count even if zero.

  - name: compute_growth
    description: Computes growth rates for a specific ward+category combination with formula transparency.
    input: >
      Dictionary with keys:
      - data: the dataset from load_dataset
      - ward: string (must match exactly)
      - category: string (must match exactly)
      - growth_type: string ('MoM' or 'YoY')
    output: >
      A list of dictionaries, one per period, each containing:
      - period: the time period
      - actual_spend: the value (or 'NULL' if missing)
      - previous_spend: the comparison value (or 'NULL')
      - growth_rate: computed percentage or 'N/A - NULL VALUE'
      - formula: string showing the calculation (e.g., "(19.7 - 14.8) / 14.8 * 100")
    error_handling: >
      If ward not found: raise ValueError with list of valid wards.
      If category not found: raise ValueError with list of valid categories.
      If growth_type not 'MoM' or 'YoY': refuse and list valid options.
      If data has nulls in the series: mark those rows, don't skip them.
