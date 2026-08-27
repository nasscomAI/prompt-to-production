# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: load_dataset
    description: Reads CSV, validates columns, reports null count and which rows before returning.
    input: file_path (string)
    output: A tuple of (validated_data (list of dicts), null_report (string))
    error_handling: Raises specific errors if the file is missing or columns are malformed. Reports exact row indices for null values in the actual_spend column.

  - name: compute_growth
    description: Takes ward + category + growth_type, returns per-period table with formula shown.
    input: data (list of dicts), ward (string), category (string), growth_type (string)
    output: A list of dicts with the computed metric (like MoM growth) and the formula shown.
    error_handling: Refuses to compute if ward/category implies data aggregation or growth_type is missing/unspecified. Flags and refuses computation for null rows.
