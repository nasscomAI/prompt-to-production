# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates columns, and reports any null values before returning the data.
    input: File path string to the CSV dataset.
    output: A validated dataset object (e.g., pandas DataFrame) and a report listing the count and specific row details of any null values found.
    error_handling: Halts execution and reports if required columns are missing. Identifies and explicitly flags all rows with null `actual_spend`, reporting the reason from the `notes` column.

  - name: compute_growth
    description: Calculates growth metrics for a specific ward and category over time based on a specified growth formula.
    input: Filtered dataset, ward string, category string, and growth_type string.
    output: A per-period table showing the computed growth and the specific formula used for each row.
    error_handling: Refuses to calculate and asks for input if `--growth-type` is not specified. Refuses to compute and returns an error if asked to aggregate across all wards or categories. Flags any null values in the target rows instead of computing a result.
