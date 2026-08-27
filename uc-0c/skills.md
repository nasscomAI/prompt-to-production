# skills.md — UC-0C Budget Data Analyst

skills:
  - name: load_dataset
    description: Ingests the ward budget CSV and identifies rows requiring special handling due to missing spend data.
    input:
      type: file_path
      format: CSV (Columns: period, ward, category, budgeted_amount, actual_spend, notes)
    output:
      type: object
      fields:
        dataframe: list of dicts
        null_rows: list of objects (indices + content of 'notes')
    error_handling: If 'actual_spend' is missing without a corresponding 'notes' entry, the row must be flagged for manual data entry.

  - name: compute_growth
    description: Calculates growth (MoM/YoY) for a single ward/category pair, surfacing the calculation logic.
    input:
      type: object
      params:
        ward: string (Exactly matches CSV ward name)
        category: string (Exactly matches CSV category name)
        growth_type: string ('MoM' or 'YoY')
    output:
      type: table
      columns: [Period, Ward, Category, Actual Spend, Formula, Result]
    error_handling: Refuses to compute if fewer than 2 data points are available for the requested period.
