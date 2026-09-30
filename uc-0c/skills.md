skills:
  - name: load_dataset
    description: Reads the budget CSV file, parses the records, and validates that the required headers are present.
    input: File path of the budget CSV (string).
    output: A list of dictionaries, where each dictionary represents a row in the CSV dataset.
    error_handling: Raises FileNotFoundError if the path is invalid. Identifies and logs the presence of null actual_spend rows.

  - name: compute_growth
    description: Evaluates and calculates period-over-period growth rates for a given ward and category while flagging null inputs.
    input: A dictionary of filters containing 'ward', 'category', 'growth_type', and the list of row dictionaries.
    output: A list of dicts containing columns period, ward, category, actual_spend, growth_rate, formula, and status.
    error_handling: Raises a ValueError or refuses to execute if ward or category represents an aggregation (like 'All' or 'Any'), or if growth_type is missing/invalid.
