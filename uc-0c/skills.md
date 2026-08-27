# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates required columns, and reports all null values before returning the data.
    input: Path to the budget CSV file (String).
    output: A dataset of budget rows and a report identifying specific null-value rows and counts.
    error_handling: Raises a FileNotFoundError if the file is missing or a ValueError if columns are invalid.

  - name: compute_growth
    description: Calculates MoM or YoY growth for a specific ward and category, flagging nulls and including the mathematical formula.
    input: Ward name (String), category name (String), growth type (String), and the dataset from load_dataset.
    output: A per-period table including actual spend, calculated growth, and the formula used.
    error_handling: Refuses calculation if growth type is missing or if unauthorized aggregation is requested.

