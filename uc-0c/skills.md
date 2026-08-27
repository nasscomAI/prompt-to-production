# skills.md

skills:
  - name: load_dataset
    description: Reads the ward budget CSV file and performs initial validation on the required columns and null values.
    input: File path to the budget CSV (e.g., `data/budget/ward_budget.csv`).
    output: A DataFrame or dictionary containing the dataset, along with a report of the number of null `actual_spend` rows and their reasons.
    error_handling: Return an error if required columns (period, ward, category, actual_spend) are missing or misnamed.

  - name: compute_growth
    description: Computes period-over-period growth (MoM) for a specific ward and category, flagging null values appropriately.
    input: Ward name, Category name, and Growth type (MoM or YoY).
    output: A list of result objects including period, actual spend, growth value, and the mathematical formula used for the calculation.
    error_handling: Refuse and report if the filtered data contains only nulls or if the growth type is unsupported.
