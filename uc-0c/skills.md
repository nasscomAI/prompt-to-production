skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates structure, and identifies null entries.
    input: File path string (e.g., ../data/budget/ward_budget.csv)
    output: Pandas DataFrame containing the data, plus a log of null counts and which specific rows are affected.
    error_handling: Raise error if critical columns (period, ward, category, budgeted_amount, actual_spend) are missing; log a report for all 5 null rows found.

  - name: compute_growth
    description: Computes period-over-period growth for a specific ward and category, flagging nulls.
    input: Ward (string), Category (string), growth-type (string, e.g., MoM)
    output: Table/CSV containing periods, actual spend, growth percentage, and the calculation formula.
    error_handling: Refuse calculation if growth-type is missing; flag null rows as 'NULL' with the reason from the 'notes' column.
