# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates required columns, and reports all null actual_spend rows with reasons before returning data.
    input: input_path (str) — path to ward_budget.csv.
    output: List of row dicts with all columns. Prints null report to stdout before returning.
    error_handling: Raises ValueError if file is empty or required columns are missing. Reports null rows but does not stop execution.

  - name: compute_growth
    description: Takes ward, category, and growth_type, returns per-period growth table with formula shown for each row.
    input: rows (list of dicts), ward (str), category (str), growth_type (str — MoM or YoY).
    output: List of dicts with fields — period, ward, category, actual_spend, growth, formula, flag.
    error_handling: Raises ValueError if growth_type is invalid or not specified. Marks rows as NOT COMPUTED if current or previous period is null. Raises ValueError if no data found for given ward and category combination.