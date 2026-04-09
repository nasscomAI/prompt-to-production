# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates columns, and reports the null count and specific rows containing nulls.
    input: File path string pointing to the CSV dataset.
    output: A list of dictionaries representing the dataset, along with a warning log of rows missing 'actual_spend' and their associated 'notes'.
    error_handling: Raises an exception if required columns (ward, category, actual_spend, notes) are missing or if the file cannot be accessed.

  - name: compute_growth
    description: Calculates the specified growth type (e.g., MoM) for a specific ward and category, strictly outputting the verbatim formula used alongside the result.
    input: The filtered dataset, ward string, category string, and the growth_type string.
    output: A list of result dictionaries containing period, calculated growth percentage, the formula string, and any null-flags.
    error_handling: Returns a refusal message if growth_type is missing/invalid, or if the user attempts to aggregate across multiple wards or categories without explicit overrides.
