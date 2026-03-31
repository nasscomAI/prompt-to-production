- name: load_dataset
  description: >
    Reads the ward budget CSV file, validates required columns, and identifies null values in actual_spend before returning structured data.
  input:
    type: string
    format: file path to CSV (ward_budget.csv)
  output:
    type: list of dictionaries
    format: >
      Each record contains period, ward, category, budgeted_amount, actual_spend, and notes,
      along with a summary of null rows including their period, ward, category, and reason.
  error_handling: >
    If the file path is invalid or the file cannot be read, return an error.
    If required columns (period, ward, category, budgeted_amount, actual_spend, notes) are missing, stop execution and report missing columns.
    If actual_spend contains null values, do not ignore them; explicitly report count and details of such rows before returning data.
    If dataset is empty or malformed, return an error and do not proceed.

- name: compute_growth
  description: >
    Computes month-over-month growth for a specified ward and category, returning a per-period table with formula included.
  input:
    type: dictionary
    format: >
      {
        "data": list of dataset records,
        "ward": string,
        "category": string,
        "growth_type": string (must be "MoM")
      }
  output:
    type: list of dictionaries
    format: >
      Each record contains period, actual_spend, growth_value, and formula_used.
      If actual_spend is null, growth_value is null and a flag with the reason from notes is included.
  error_handling: >
    If ward or category is not found in the dataset, return an error.
    If growth_type is missing or not "MoM", refuse to compute and ask for correct specification.
    If attempting to aggregate across wards or categories, refuse execution.
    If previous period data is missing or null, do not compute growth for that period and flag it.
    If actual_spend is null for any row, do not compute growth and include the null reason from notes.
    Ensure no silent assumptions are made about formulas; only compute explicitly requested growth type.