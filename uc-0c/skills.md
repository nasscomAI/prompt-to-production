skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates required structural columns, and explicitly reports the total null count and specific rows containing null values before returning the data for processing.
    input: CSV file path (string)
    output: Validated dataset object (e.g., pandas DataFrame) paired with a summary report detailing null counts and specific null row identifiers.
    error_handling: If required columns (period, ward, category, budgeted_amount, actual_spend, notes) are missing, or the file is unreadable, halt execution and return a descriptive error detailing the missing elements.

  - name: compute_growth
    description: Calculates the specified growth metric for a given ward and category combination, outputting a per-period table that explicitly includes the calculation formula for transparency.
    input: Validated dataset (object), ward (string), category (string), and growth_type (string).
    output: A per-period data table containing the period, ward, category, actual spend, computed growth metric, and the exact formula used.
    error_handling: If actual_spend is null for a period, flag the row with the reason from the notes column instead of computing a value. If growth_type is missing or invalid, halt and request clarification rather than guessing.
