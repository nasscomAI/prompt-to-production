skills:
  - name: load_dataset
    description: Reads the budget CSV, validates columns, and explicitly identifies any null values before proceeding.
    input: File path (string) to the input budget CSV.
    output: A validated dataset object/list, along with a report detailing the total null count and the specific rows containing nulls (including the 'notes' column reason).
    error_handling: If the file is missing or lacks the required columns (period, ward, category, budgeted_amount, actual_spend, notes), halt execution and raise an error.

  - name: compute_growth
    description: Takes the validated dataset, a specified ward, a category, and a required growth_type, computing the growth per period while displaying the formula used.
    input: Validated dataset structured data, ward (string), category (string), and growth_type (string, e.g., MoM or YoY).
    output: A per-period table (list of rows) showing the calculated growth, the parsed null flags, and explicitly showing the mathematical formula used for each row's result.
    error_handling: If the growth_type is missing, or if an aggregation across multiple wards/categories is requested, immediately refuse the operation and return an explicit refusal error message without computing. If a target row has a null actual_spend, flag the row, cite the reason, and return "not computed" instead of a number.
