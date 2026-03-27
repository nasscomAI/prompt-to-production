# skills.md

skills:
  - name: read_budget_data
    description: Reads municipal ward budget data from CSV.
    input: Path to ward_budget.csv file.
    output: List of rows containing ward budget records.
    error_handling: If file cannot be read, return empty dataset.

  - name: calculate_growth
    description: Calculates growth values for each ward and category.
    input: Budget dataset rows.
    output: Dataset containing calculated growth values.
    error_handling: If numeric values are missing, mark row with DATA_MISSING flag.