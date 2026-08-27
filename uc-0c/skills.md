# skills.md

skills:
  - name: load_dataset
    description: Reads CSV file, validates columns, reports null count and which rows have null actual_spend
    input: "input_path (str): path to budget CSV file"
    output: "dict with keys: data (list of dicts), columns (list), null_rows (list of dicts with period, ward, category, notes)"
    error_handling: "If file not found, raise FileNotFoundError. If required columns missing, raise ValueError."

  - name: compute_growth
    description: Calculates MoM or YoY growth for a specific ward and category, handling nulls properly
    input: "data (list), ward (str), category (str), growth_type (str: 'MoM' or 'YoY')"
    output: "list of dicts with keys: period, actual_spend, growth_pct, formula, null_flag, null_reason"
    error_handling: "If growth_type not specified, raise ValueError('growth_type required'). If ward/category not found, raise ValueError."
