# skills.md — UC-0C Financial Data Skills

skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates required columns, and isolates deliberate null actual_spend rows along with notes.
    input: File path string pointing to ward_budget.csv.
    output: Parsed list of dictionaries containing validated records and flagged null logs.
    error_handling: Raises FileNotFoundError or KeyError if expected columns are missing or unreadable.

  - name: compute_growth
    description: Calculates month-over-month (MoM) growth for a specific ward and category while displaying calculation formulas and skipping missing values.
    input: Target ward name, category name, growth_type, and loaded dataset.
    output: List of dictionaries formatted for CSV export including period, actual_spend, growth_percent, formula, and notes.
    error_handling: Flags missing values as 'NULL - Not Computed' and refuses execution if growth_type or target scopes are invalid.