# skills.md

skills:
  - name: load_dataset
    description: Reads and validates the ward budget CSV, precisely identifying and reporting all null values before data processing.
    input: File path to the ward budget CSV.
    output: A cleaned list of dictionary rows including period, ward, category, budgeted_amount, actual_spend, and notes.
    error_handling: Notifies the user of exact rows and reasons for null values based on the 'notes' column.

  - name: compute_growth
    description: Performs per-period growth calculations (MoM or YoY) for a specific ward and category while maintaining formula transparency.
    input: Ward name, category name, and growth type (MoM/YoY).
    output: A table showing period, actual spend, growth percentage, and the calculation formula used.
    error_handling: Explicitly flags null periods as "NOT COMPUTED" and cites the reason instead of guessing or interpolating.
