skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates expected columns, and reports the null count and exactly which rows have missing data before returning the dataset.
    input: File path to the dataset (e.g., `../data/budget/ward_budget.csv`).
    output: Validated dataset (e.g., DataFrame) alongside a detailed report flagging the null rows and their associated notes.
    error_handling: Raises a clear error if the file is unreadable or expected columns (`period`, `ward`, `category`, `budgeted_amount`, `actual_spend`, `notes`) are missing.

  - name: compute_growth
    description: Calculates per-period growth (e.g., MoM or YoY) for a specific, isolated ward and category.
    input: Validated dataset, `ward` (string), `category` (string), and `growth_type` (string).
    output: A per-period table showing calculated growth along with the exact formula used for each row.
    error_handling: Refuses calculation if `growth_type` is not provided (asks instead) or if asked to aggregate multiple wards/categories. For rows with null actuals, flags the response with the null reason instead of attempting a calculation.
