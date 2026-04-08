# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

- name: load_dataset
  description: >
    Reads the ward budget CSV file, validates required columns, and identifies null rows before returning structured data.
  input: >
    file_path: string — path to the CSV file containing ward budget data.
  output: >
    dataset: list of records with fields (period, ward, category, budgeted_amount, actual_spend, notes);
    null_report: list of rows where actual_spend is null along with period, ward, category, and notes;
    summary: total rows count and null count.
  error_handling: >
    If file is missing or unreadable, raise an error.
    If required columns are missing, stop execution and report missing columns.
    If dataset is empty, return error.
    If null values are found, do not ignore them; return them in null_report before any computation.

- name: compute_growth
  description: >
    Computes per-period growth (e.g., MoM) for a specific ward and category using actual spend values.
  input: >
    dataset: validated dataset from load_dataset;
    ward: string — selected ward;
    category: string — selected category;
    growth_type: string — type of growth calculation (e.g., MoM).
  output: >
    growth_table: list of rows containing period, actual_spend, growth_percentage, and formula_used;
    flagged_rows: rows where growth could not be computed due to null values.
  error_handling: >
    If ward or category not found, return error.
    If growth_type is missing or invalid, refuse and request valid input.
    If actual_spend is null for any period, flag the row and do not compute growth.
    If previous period value is missing (needed for MoM), skip calculation and flag it.
    If attempt is made to aggregate across wards or categories, refuse execution.
