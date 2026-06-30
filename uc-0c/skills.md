# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: load_dataset
    description: Load and validate the ward budget dataset.
    input: CSV file path.
    output: Validated dataset with null rows identified.
    error_handling: Raise an error if required columns are missing.

  - name: compute_growth
    description: Compute month-over-month growth for a selected ward and category.
    input: Dataset, ward, category and growth type.
    output: Growth table including formula and null handling.
    error_handling: Refuse computation if growth type is missing.
