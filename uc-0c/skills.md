# skills.md — UC-0C Budget Growth Calculator

skills:
  - name: load_dataset
    description: Ingests ward_budget.csv, validates column schema, and inspects records for missing or null actual_spend rows.
    input: file_path (str) - path to budget CSV file
    output: tuple (rows: list, null_rows: list) - parsed rows and a detailed inventory of null records with notes
    error_handling: Raises FileNotFoundError if missing; raises ValueError if required columns are absent.

  - name: compute_growth
    description: Computes period-over-period growth rates for a specific ward and category, returning formulas and flags for each period.
    input: rows (list), ward (str), category (str), growth_type (str - 'MoM' or 'YoY')
    output: list of dict records with period, spend, growth rate, formula, and status flags
    error_handling: Refuses calculation and raises ValueError if cross-ward aggregation is attempted or growth_type is omitted.
