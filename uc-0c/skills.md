skills:

* name: load_dataset
  description: "Loads the ward budget CSV file, validates required columns, and identifies all null actual_spend rows with their context."
  input: "File path string to a CSV file containing columns: period, ward, category, budgeted_amount, actual_spend, notes."
  output: "A structured dataset (list of records or dataframe) along with a report of null rows including period, ward, category, and notes."
  error_handling: "If the file path is invalid or unreadable, abort with an error; if required columns are missing, abort; if dataset is empty, abort; if null values exist, they must be explicitly reported and not silently ignored."

* name: compute_growth
  description: "Computes per-period growth for a specified ward and category using the specified growth type while preserving granularity and showing formulas."
  input: "Structured dataset plus parameters: ward (string), category (string), growth_type (string: MoM or YoY)."
  output: "A per-period table containing period, actual_spend, computed growth value, and the explicit formula used for each row, with null cases flagged."
  error_handling: "If ward or category does not exist, abort with an error; if growth_type is missing or invalid, refuse to proceed; if null actual_spend is encountered in current or comparison period, flag the row and skip computation; if aggregation across wards or categories is attempted, refuse execution; if insufficient data exists for growth calculation, mark as not computed."
