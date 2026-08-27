# skills.md

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates the required columns, and reports the null actual_spend rows before returning the dataset.
    input: A CSV file path, expected here to be ../data/budget/ward_budget.csv.
    output: A validated dataset with columns period, ward, category, budgeted_amount, actual_spend, and notes, plus a null report containing the null count and the specific ward-category-period rows where actual_spend is blank.
    error_handling: Refuses with a clear validation error if the file is missing, unreadable, missing required columns, or if null actual_spend rows cannot be identified and reported before computation.

  - name: compute_growth
    description: Takes a validated dataset plus ward, category, and growth_type and returns a per-period growth table with the formula shown for each row.
    input: The validated dataset from load_dataset together with one ward, one category, and an explicit growth_type.
    output: A per-period table for the requested ward and category that includes period, actual_spend, growth result when computable, formula used for that row, and a flag plus null reason when actual_spend is blank.
    error_handling: Refuses if growth_type is not provided, if the request implies all-ward or cross-category aggregation, or if a row with null actual_spend would be computed instead of flagged with its notes reason.
