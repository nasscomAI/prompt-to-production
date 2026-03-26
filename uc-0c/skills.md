skills:
  - name: load_dataset
    description: Reads the budget dataset and identifies rows with missing actual_spend values.
    input: Path to the ward_budget.csv dataset.
    output: Structured dataset and a report of rows containing null values.
    error_handling: If required columns are missing or file cannot be read, return an error and stop processing.

  - name: compute_growth
    description: Computes growth values for a specified ward and category using the requested growth type.
    input: Filtered dataset, ward name, category name, growth type.
    output: Per-period growth table including formula used.
    error_handling: If null values are encountered in a calculation period, flag the row instead of computing growth.