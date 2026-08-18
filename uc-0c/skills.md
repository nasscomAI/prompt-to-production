skills:
  - name: load_dataset
    description: Ingests ward budget CSV data, validates required columns, identifies all null rows, and generates a pre-computation null audit report.
    input: input_path (str - path to ward_budget.csv)
    output: tuple of (records: list of dicts, null_report: list of dicts describing null rows and notes)
    error_handling: Raises ValueError if required columns are missing; safely records unparseable values as null with warning flags.

  - name: compute_growth
    description: Computes period-over-period expenditure growth strictly scoped within a single ward and category, returning formatted records with formulas and null flags.
    input: records (list of dicts), ward (str), category (str), growth_type (str - e.g. 'MoM' or 'YoY')
    output: list of dicts containing {period, ward, category, budgeted_amount, actual_spend, growth_pct, formula, flag, notes}
    error_handling: Refuses cross-ward aggregation; flags periods where actual_spend or previous period spend is null as 'NULL_SPEND' or 'PRIOR_NULL'.

