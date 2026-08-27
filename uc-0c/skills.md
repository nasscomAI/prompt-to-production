skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates its columns, and reports any rows containing null actual spend values.
    input: file_path (string) - Path to the budget CSV file.
    output: records (list of dictionaries representing the budget rows).
    error_handling: If the file is missing, unreadable, or lacks required columns, prints an error to stderr and exits non-zero.

  - name: compute_growth
    description: Computes MoM growth for a specific ward and category, returning a per-period table with formulas and flagged nulls.
    input: records (list of dicts), ward (string), category (string), growth_type (string).
    output: growth_table (list of dicts containing computed growth and formula).
    error_handling: If ward, category, or growth_type is missing or invalid, or if asked to aggregate multiple categories/wards, prints an error to stderr and exits non-zero.
