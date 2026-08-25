# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Read the budget CSV, validate columns, and report the null rows before any computation.
    input: Path to ward_budget.csv.
    output: A dict with the parsed rows keyed by (period, ward, category), the set of expected columns,
      and a report of every null actual_spend row with its notes reason.
    error_handling: Raises if required columns (period, ward, category, budgeted_amount, actual_spend, notes)
      are missing; never silently drops a null row from the report.

  - name: compute_growth
    description: Compute per-period growth for one ward+category using the requested growth type.
    input: The loaded dataset, a single ward name, a single category name, and a growth type (MoM or YoY).
    output: A per-period table with columns: period, ward, category, actual_spend, previous_actual_spend,
      growth_pct, formula, status, notes. Growth is only computed for the requested ward+category; every
      row carries the formula that produced its number.
    error_handling: Refuses (returns no table) if the scope is missing or set to 'All'; refuses if the
      growth type is missing or unsupported; marks rows with no reference period or null spend as
      not-computed instead of inventing a value.
