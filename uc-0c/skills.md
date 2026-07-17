skills:
  - name: load_dataset
    description: Reads a CSV budget file, validates columns, and reports details of any null rows found.
    input:
      type: string
      format: "The path to the input CSV budget file (e.g. ward_budget.csv)."
    output:
      type: list of dicts
      format: "A list of dictionaries representing valid rows of the CSV, each containing period, ward, category, budgeted_amount, actual_spend, and notes."
    error_handling: >
      If any columns are missing, raises a ValueError. Flags and reports the total count of null values in actual_spend, listing each row's details and the notes explaining the reason.

  - name: compute_growth
    description: Computes month-over-month (MoM) growth of actual spend for a specified ward and category, returning a per-period table with formulas.
    input:
      type: parameters
      format: "dataset: list of dicts, ward: string, category: string, growth_type: string"
    output:
      type: list of dicts
      format: "A list of dictionary rows including period, actual_spend, growth, formula, and notes."
    error_handling: >
      Refuses and raises a ValueError if growth_type is missing or invalid. Refuses if ward or category is missing or set to aggregate over all entries. For any period where current or previous spend is null, sets growth to 'NULL' and cites the reason from notes.
