skills:
  - name: load_dataset
    description: Reads the ward budget CSV file, validates the column structure, identifies any null actual_spend rows, and returns the list of rows.
    input:
      type: str
      format: Path to the budget CSV file.
    output:
      type: list
      format: A list of dictionaries representing the CSV rows.
    error_handling:
      rules:
        - "If the file is not found, raise FileNotFoundError."
        - "If required columns (period, ward, category, budgeted_amount, actual_spend) are missing, raise ValueError."

  - name: compute_growth
    description: Filters rows by ward and category, and calculates MoM or YoY spend growth for each period, formatting the output with actual spend, growth percentage, the formula, and flag/notes.
    input:
      type: dict
      format: A dictionary containing 'rows' (list), 'ward' (string), 'category' (string), and 'growth_type' (string).
    output:
      type: list
      format: A list of dictionaries representing the per-period growth rows.
    error_handling:
      rules:
        - "If ward, category, or growth_type parameters are empty, missing, or represent a request for global/aggregated data (like 'All' or 'Any'), refuse execution and raise a ValueError."
        - "If the growth_type is not 'MoM' or 'YoY', raise ValueError."
        - "If a row has a null actual_spend, output actual_spend as NULL, growth as n/a, formula as n/a, and report the notes."
