# skills.md

skills:
  - name: load_dataset
    description: Reads the CSV dataset, validates the required columns exist, and reports the count and locations of any missing data values before proceeding.
    input: file_path (string) to the CSV data.
    output: A parsed data structure and a summary object listing total rows and any rows with null actual_spend values including their notes.
    error_handling: Halts and raises an error if the fundamental columns (period, ward, category, budgeted_amount, actual_spend) are missing.

  - name: compute_growth
    description: Takes the filtered dataset for a specific ward and category, and applies the requested growth_type calculation.
    input: filtered_data (list of dicts), growth_type (string, e.g., 'MoM').
    output: A list of dicts representing the computation per period, including the formula used, and explicitly flagging skipped periods due to null actuals.
    error_handling: Refuses to execute if the growth_type is invalid or missing, prompting the user for clarity.
