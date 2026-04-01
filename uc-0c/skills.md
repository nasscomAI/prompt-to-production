# skills.md — UC-0C Budget Analyst

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates structure, and identifies all rows with null `actual_spend` values.
    input: File path to `ward_budget.csv`.
    output: A list of dictionaries representing the dataset and a summary of identified nulls.
    error_handling: Reports columns missing or malformed data types.

  - name: compute_growth
    description: Filters data by ward and category, then calculates growth (MoM) between consecutive periods.
    input: Dataset list, target ward name, target category name, and growth type (e.g., MoM).
    output: A list of objects containing period, actual spend, growth percentage, and the calculation formula used.
    error_handling: Refuses calculation for any period where the current or previous value is null, instead reporting the reason from the notes.
