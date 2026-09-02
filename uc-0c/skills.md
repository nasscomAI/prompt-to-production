skills:
  - name: load_dataset
    description: Reads and validates the ward budget CSV, verifies required columns, tallies total row count, audits all null actual_spend rows without zero-imputation, and reports their documented reasons.
    input: file_path (str) path pointing to ward_budget.csv.
    output: dict containing validated dataset rows (list of dicts with types preserved and nulls explicitly kept as None) and an audit report of all null actual_spend rows (period, ward, category, notes).
    error_handling: Raises FileNotFoundError if file is missing; raises ValueError if required columns (period, ward, category, budgeted_amount, actual_spend, notes) are absent; strictly preserves null values as None without converting to zero or dropping rows.

  - name: compute_growth
    description: Computes period-over-period expenditure growth strictly for a specified ward and category combination, outputting a per-period table with explicit formulas, audit trails, and null flagging.
    input: dataset (list of dicts), ward (str, e.g., 'Ward 1 – Kasba'), category (str, e.g., 'Roads & Pothole Repair'), and growth_type (str, e.g., 'MoM').
    output: list of dicts representing a per-period table with columns period, ward, category, actual_spend, growth_pct, formula, and notes.
    error_handling: If growth_type is missing or empty, refuses execution and prompts user; if user requests cross-ward or cross-category aggregation, refuses execution; if current or preceding actual_spend is null, sets growth_pct to None, flags status as UNCOMPUTABLE, preserves notes explanation, and avoids zero-division or imputation.
