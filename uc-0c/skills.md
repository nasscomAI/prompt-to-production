# skills.md — UC-0C Budget Analyst

skills:
  - name: load_dataset
    description: Loads a financial CSV dataset and performs a strict audit for missing values and column integrity.
    input: File path to the budget dataset (e.g., ward_budget.csv).
    output: A data collection plus a validation report identifying the count and specific locations (period/ward) of all null 'actual_spend' entries.
    error_handling: Refuses to proceed if required columns (ward, category, actual_spend) are missing or mislabeled.

  - name: compute_growth
    description: Calculates growth metrics (MoM/YoY) for a filtered subset of data while providing full formula transparency.
    input: Ward name, Category name, and Growth Type (MoM or YoY).
    output: A table containing periods, actual spend values, growth percentages, and the explicit formula used for every calculation.
    error_handling: Skips growth calculation for periods involving a null 'actual_spend' and instead outputs the reason from the 'notes' column.
