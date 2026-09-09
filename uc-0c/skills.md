# skills.md — UC-0C Budget Growth Calculator

skills:
  - name: load_dataset
    description: Reads the budget CSV dataset, validates schema integrity, and reports all null rows and reasons before returning data.
    input: File path to ward_budget.csv.
    output: Tuple containing list of row dicts and list of detected null row objects with reasons from notes column.
    error_handling: Raises FileNotFoundError if CSV missing; validates required columns (period, ward, category, budgeted_amount, actual_spend, notes); logs null count explicitly without discarding any rows.

  - name: compute_growth
    description: Computes period-over-period spend growth for a specific ward and category, annotating each period with the formula used and flagging nulls.
    input: Rows list, target ward string, target category string, growth_type string ('MoM' or 'YoY').
    output: List of structured result dicts containing period, ward, category, budgeted, actual, growth, formula, and flag/status.
    error_handling: Refuses if ward is "All" or empty; refuses if growth_type is missing or invalid; does not compute growth on null rows (marks as NULL_VALUE with source note).
