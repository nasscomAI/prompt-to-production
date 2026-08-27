# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: load_dataset
    description: Reads the CSV dataset, validates columns, and explicitly reports the null count and specific null rows before returning the data.
    input: File path to the dataset (specifically ../data/budget/ward_budget.csv).
    output: Structured data object containing the validated rows, along with a metadata report of null counts and their locations.
    error_handling: If columns are missing or unreadable, return a schema validation error. If the file is not found, return 'Dataset file not found or inaccessible.'

  - name: compute_growth
    description: Computes growth metrics for a specific ward and category based on the requested growth type, showing the formula used.
    input: The loaded dataset, ward name, category name, and growth_type (e.g., MoM).
    output: A per-period table saved to uc-0c/growth_output.csv containing the computed metric and the exact formula used for every output row.
    error_handling: If growth_type is missing, immediately refuse and ask the user (never guess). If asked to aggregate across wards or categories without explicit instruction, refuse the request. If actual_spend is null for a row, flag it using the notes column instead of computing a value.
