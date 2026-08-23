# skills.md — UC-0C Budget Growth Calculator Skills

skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates required columns (period, ward, category, budgeted_amount, actual_spend, notes), audits deliberate null actual_spend rows, and returns data along with a null report.
    input: file_path (str path to ward_budget.csv).
    output: Tuple containing list of row dictionaries and list of identified null row dictionaries.
    error_handling: Raises FileNotFoundError if CSV missing, or ValueError if required header columns are missing.

  - name: compute_growth
    description: Takes filtered dataset rows for a specific ward, category, and growth_type (MoM), calculates percentage growth, formats formula display, and flags null periods without corrupting math.
    input: rows (list of row dicts), ward (str), category (str), growth_type (str).
    output: List of dictionaries representing the calculated growth output table.
    error_handling: Refuses calculation if growth_type is unstated or if ward/category filters match zero rows.
