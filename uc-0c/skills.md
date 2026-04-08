# skills.md — UC-0C Budget Growth Calculator

skills:
  - name: load_dataset
    description: Reads the ward budget CSV file, validates required columns, and returns data as a list of dictionaries with null count reported.
    input: File path (string) to ward_budget.csv
    output: Dictionary with keys: 'data' (list of dicts), 'null_count' (int), 'null_rows' (list of dicts with period, ward, category, notes)
    error_handling: >
      If file not found: raise FileNotFoundError.
      If missing required columns (period, ward, category, actual_spend, notes): raise ValueError listing missing columns.
      Reports null_count and null_rows before returning.

  - name: compute_growth
    description: Computes MoM or YoY growth for a specific ward + category combination, returning per-period table with formula shown.
    input: data (list of dicts), ward (string), category (string), growth_type (string: "MoM" or "YoY")
    output: List of dicts with keys: period, actual_spend, growth_rate, formula, flag. Includes header row.
    error_handling: >
      If ward not found in data: raise ValueError with message listing available wards.
      If category not found in data: raise ValueError with message listing available categories.
      If growth_type is not "MoM" or "YoY": raise ValueError with message "Please specify --growth-type MoM or YoY".
      If null actual_spend encountered: include row with flag=NULL_REASON (from notes) and growth_rate=None.
      If insufficient periods: raise ValueError with minimum periods required.
