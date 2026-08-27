# skills.md

skills:
  - name: load_dataset
    description: Reads CSV, validates columns, and reports null count/rows before returning data.
    input: File path string (path to ward_budget.csv).
    output: Dataset object/dataframe and a pre-computation report of null spending entries.
    error_handling: Refuses if required columns are missing or file is inaccessible.

  - name: compute_growth
    description: Computes categorical growth (MoM/YoY) for a specific ward, returning results with explicit formulas.
    input: Ward name (string), Category (string), and Growth type (string).
    output: Per-period growth table with a "Formula" column showing the calculation logic used.
    error_handling: Refuses to compute if growth_type is missing or if input is an aggregated request.
