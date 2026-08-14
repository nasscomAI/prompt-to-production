# skills.md — UC-0C Financial Growth Skills

skills:
  - name: load_dataset
    description: Reads the budget CSV dataset, validates schema headers, and pre-audits null actual_spend rows alongside their explanatory notes.
    input: File path input_path (str, e.g. path to ward_budget.csv).
    output: Dataset records (list of dicts) and null audit report specifying affected period, ward, category, and notes reason.
    error_handling: Raises FileNotFoundError if CSV path is invalid; raises ValueError if required columns are missing.

  - name: compute_growth
    description: Computes per-period growth for a specific ward and category using the designated growth formula, attaching explicit formulas and null flags per row.
    input: Dataset records, ward name (str), category name (str), and growth_type (str: MoM|YoY).
    output: List of output dictionaries containing period, ward, category, actual_spend, growth_rate, formula_used, and notes.
    error_handling: Refuses execution if growth_type is omitted or if cross-ward aggregation is requested; sets growth as NULL/Uncomputable for null spend rows.

