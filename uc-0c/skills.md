# skills.md — UC-0C Budget Analysis Skills

skills:
  - name: load_dataset
    description: Reads the CSV budget data, validates required columns, and proactively reports the location and count of null spend rows.
    input: File path to ward_budget.csv.
    output: Structured dataset (dataframe or list of dicts) with metadata on null rows.
    error_handling: Refuses to proceed if required columns (period, ward, category, actual_spend) are missing.

  - name: compute_growth
    description: Calculates MoM or YoY growth for a specific ward and category, incorporating null flagging and formula tracking.
    input: Ward name, Category name, Growth type (MoM/YoY), Dataset.
    output: Table containing period, actual_spend, growth_value, and the formula used.
    error_handling: Returns the reason from the 'notes' column instead of a value for null spend rows.
