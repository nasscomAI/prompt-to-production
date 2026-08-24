skills:
  - name: load_dataset
    description: Reads ward_budget.csv, validates required columns, and reports null count with specific row details before returning structured data.
    input:
      type: file_path
      format: "string — absolute or relative path to ward_budget.csv (e.g., '../data/budget/ward_budget.csv')"
    output:
      type: structured_dataset
      format: "JSON object with 'rows' (list of dicts with period, ward, category, budgeted_amount, actual_spend, notes), 'null_report' (list of dicts with period, ward, category, reason from notes), 'column_validation' (bool)"
    error_handling:
      - If file does not exist: raise FileNotFoundError with path
      - If required columns missing: raise ValueError listing missing columns
      - If actual_spend nulls found: include in null_report with period, ward, category, and notes reason — do not silently drop
      - If CSV malformed: raise ParseError with line number

  - name: compute_growth
    description: Computes per-period growth for a specific ward+category+growth_type, returning a table with formula shown per row.
    input:
      type: compute_request
      format: "JSON object with 'rows' (from load_dataset), 'ward' (string, exact match), 'category' (string, exact match), 'growth_type' (string: 'MoM' or 'YoY')"
    output:
      type: growth_table
      format: "CSV written to uc-0c/growth_output.csv with columns: period, actual_spend, growth_pct, formula_used, null_flag, null_reason; one row per period for the ward+category"
    error_handling:
      - If ward not found in data: raise ValueError with available wards
      - If category not found for ward: raise ValueError with available categories
      - If growth_type not 'MoM' or 'YoY': raise ValueError — never guess, refuse and ask
      - If actual_spend is null for a period: set growth_pct to 'NULL', null_flag to true, null_reason from notes, formula_used to 'N/A — null actual_spend'
      - If requested to aggregate across wards/categories: raise AggregationRefusedError