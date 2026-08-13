# skills.md — UC-0C Financial Growth Analysis Skills

skills:
  - name: load_dataset
    description: Reads the budget CSV dataset, validates required columns, identifies and reports all null actual_spend rows along with their corresponding notes before returning structured rows.
    input: File path string pointing to ward_budget.csv.
    output: Tuple containing list of dataset dictionaries and list of identified null record reports.
    error_handling: Raises FileNotFoundError if CSV missing or ValueError if required headers are absent.

  - name: compute_growth
    description: Filters dataset by specific ward and category, calculates period-over-period growth (e.g. MoM), attaches exact formula string to each row, and flags null spend rows with note explanations.
    input: Dataset list, ward string, category string, growth_type string ('MoM' or 'YoY').
    output: List of formatted output dictionaries containing period, ward, category, budgeted_amount, actual_spend, growth, formula, notes, flag.
    error_handling: Refuses calculation if growth_type is missing or if ward/category arguments attempt unauthorized all-ward aggregation.
