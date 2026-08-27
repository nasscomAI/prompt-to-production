skills:
  - name: load_dataset
    description: Reads the provided CSV dataset, validates required columns, and flags any rows containing null actual_spend values along with their notes before returning the data.
    input: Local file path to the CSV dataset (string, e.g., `../data/budget/ward_budget.csv`).
    output: A validated dataset structure (e.g., pandas DataFrame) alongside a report of the total null count and details of the specific rows with missing actual_spend.
    error_handling: Throws a clear error if the file path is invalid, or if any required columns (period, ward, category, budgeted_amount, actual_spend, notes) are missing.

  - name: compute_growth
    description: Calculates localized spend growth metrics (e.g., MoM or YoY) for a specific ward and category without unauthorized cross-aggregation, actively reporting null reasons.
    input: ward (string), category (string), growth_type (string), and the validated dataset data structure.
    output: A detailed per-period table displaying the period, ward, category, budgeted_amount, actual_spend, the computed growth metric, and the exact mathematical formula used for each row.
    error_handling: Refuses operation and explicitly prompts the user if `growth_type` is not specified or ambiguous; refuses to operate across all wards/categories without explicit instructions; and flags null `actual_spend` rows with the precise reason from the notes column instead of guessing values.
