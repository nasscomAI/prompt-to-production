# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_budget_data
    description: Loads budget CSV and returns structured data filtered by ward and category.
    input: Path to CSV file (str), ward name (str), category name (str)
    output: List of dictionaries with period, ward, category, budgeted_amount, actual_spend, notes
    error_handling: If file not found, raise FileNotFoundError. If ward/category not found, return empty list.

  - name: calculate_growth
    description: Calculates month-over-month growth rates for the filtered budget data.
    input: List of budget records sorted by period (list)
    output: List of dictionaries with period, actual_spend, mom_growth, and flag for nulls
    error_handling: If data is empty, return empty list. If previous month is null, flag current as NULL.
