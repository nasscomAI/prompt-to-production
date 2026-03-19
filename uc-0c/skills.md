# skills.md — UC-0C Budget Growth Calculator

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates columns, and reports null actual_spend counts and which rows are affected.
    input: file_path (str) — path to ward_budget.csv.
    output: A pandas-free list of dicts representing rows, plus a list of null-row reports with period, ward, category, and notes.
    error_handling: >
      If the file is missing or has unexpected columns, prints an error and
      exits. Reports all null rows to stdout before returning data.

  - name: compute_growth
    description: Takes ward + category + growth_type, filters data, and returns a per-period table with formula shown.
    input: data (list of dicts), ward (str), category (str), growth_type (str — MoM or YoY).
    output: A list of dicts with period, actual_spend, growth_rate, formula, and null_flag columns.
    error_handling: >
      If ward or category is not found in data, reports available values and
      exits. If growth_type is unrecognised, refuses and lists valid options.
      Null actual_spend rows are flagged and excluded from computation.
