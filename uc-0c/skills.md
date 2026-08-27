skills:
  - name: load_dataset
    description: Reads the CSV dataset, validates schema, and reports null values with row details.
    input: >
      File path (string) to CSV file containing columns:
      period, ward, category, budgeted_amount, actual_spend, notes
    output: >
      Parsed dataset (list/dictionary or DataFrame) +
      summary of null rows (count, location, reason)
    error_handling: >
      If file not found → raise error;
      If required columns missing → raise schema validation error;
      If malformed data → report row-level issues and stop execution.

  - name: compute_growth
    description: Computes growth (e.g., MoM) for a specific ward and category across periods.
    input: >
      Dataset (validated), ward (string), category (string),
      growth_type (string: MoM or YoY)
    output: >
      Table (list of rows) where each row contains:
      period, actual_spend, growth_value, formula_used OR null_flag_with_reason
    error_handling: >
      If ward/category not found → raise error;
      If growth_type invalid/missing → refuse execution;
      If previous period value is null → flag growth as not computable;
      If current value is null → flag with reason from notes and skip computation.