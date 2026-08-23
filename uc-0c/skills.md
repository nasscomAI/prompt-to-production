# skills.md

skills:
  - name: load_dataset
    description: >
      Load and validate the budget CSV file. Identify all columns, count rows, find null
      actual_spend values, and report the null count with details before returning data.
    input: >
      File path (string). Must be a CSV with columns: period, ward, category, budgeted_amount,
      actual_spend, notes.
    output: >
      Dictionary with keys: 'data' (list of dicts), 'total_rows' (int), 'null_rows' (list
      of dicts with period, ward, category, reason). Example null_row dict: 
      {'period': '2024-03', 'ward': 'Ward 2 – Shivajinagar', 'category': 'Drainage & Flooding', 'reason': 'Data not submitted by ward office'}
    error_handling: >
      If file not found, raise FileNotFoundError with path. If columns missing, raise ValueError
      listing missing columns. If no data rows, raise ValueError 'CSV is empty'.

  - name: compute_growth
    description: >
      Compute month-over-month or year-over-year growth for a specific ward-category pair.
      Return a table with period, actual_spend, prior_value, growth_percentage, and formula.
    input: >
      Dictionary with keys: 'data' (list of dicts from load_dataset), 'ward' (string),
      'category' (string), 'growth_type' (string: 'MoM' or 'YoY'). 
      Example: {'data': [...], 'ward': 'Ward 1 – Kasba', 'category': 'Roads & Pothole Repair', 'growth_type': 'MoM'}
    output: >
      List of dicts with keys: 'period', 'actual_spend' (float or 'NULL'), 'prior_value' (float or 'NULL'),
      'growth_percentage' (float or 'NULL'), 'formula' (string), 'note' (string if null, else empty).
      Example row: {'period': '2024-02', 'actual_spend': 12.2, 'prior_value': 13.3, 'growth_percentage': -8.3, 
      'formula': '(12.2 - 13.3) / 13.3 * 100', 'note': ''}
      For null rows: {'period': '2024-03', 'actual_spend': 'NULL', 'prior_value': None, 'growth_percentage': None,
      'formula': '', 'note': 'Data not submitted by ward office'}
    error_handling: >
      If ward not in data, raise ValueError 'Ward not found: <ward>'. If category not found for ward,
      raise ValueError 'Category not found for ward: <category>'. If growth_type not 'MoM' or 'YoY',
      raise ValueError 'growth_type must be MoM or YoY, got: <growth_type>'. Return at least 2 months
      (since growth needs a prior value).
