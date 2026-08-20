skills:
  - name: load_dataset
    description: Reads the input CSV budget record, validates its structure, and reports any null `actual_spend` occurrences before returning the data.
    input: File path to the dataset CSV (e.g., ward_budget.csv)
    output: Validated data object containing the budget records, along with a report of the null count and specific rows holding null values.
    error_handling: Raises an explicit error if expected columns are missing or if the file cannot be read. Does not attempt to guess missing values or drop null rows silently.

  - name: compute_growth
    description: Processes budget records to output a per-period table calculating specified type of growth for an isolated ward and category.
    input: Target `ward` (string), target `category` (string), and explicitly declared `growth_type` (string, e.g., 'MoM').
    output: A per-period table containing period, budgeted_amount, actual_spend, computed growth percentage, and the exact formula used for every row.
    error_handling: Strictly refuses to guess if `--growth-type` isn't provided. Refuses to aggregate metrics across multiple wards or categories if requested. Flags null row scenarios with the specific reason from the `notes` column instead of calculating or throwing a math error.
