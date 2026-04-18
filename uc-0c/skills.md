- name: load_dataset
  description: Reads the ward budget CSV dataset, validates required columns, and identifies null values.
  input:
    type: string
    format: file path to CSV dataset
  output:
    type: object
    format: validated dataset with metadata including null row details
  error_handling:
    - If file path is invalid, return an error and stop execution
    - If required columns are missing, return an error specifying missing columns
    - If null values are present in actual_spend, identify and report all such rows along with notes before returning dataset

- name: compute_growth
  description: Computes growth metrics (MoM or YoY) for a specific ward and category and returns a per-period table.
  input:
    type: object
    format: dataset along with ward, category, and growth_type parameters
  output:
    type: table
    format: per-period rows including actual spend, computed growth, and formula used
  error_handling:
    - If ward or category is not found, return an error
    - If growth_type is missing or invalid, refuse to compute and ask for valid input
    - If null values are encountered for a period, do not compute growth for that period and flag it with reason from notes
    - If computation attempts aggregation across wards or categories, refuse execution

    
