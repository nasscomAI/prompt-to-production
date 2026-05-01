skills:
  - name: load_dataset
    description: Reads the budget CSV, validates columns, and reports null count and which rows before returning the data.
    input: File path to the budget CSV.
    output: A structured dataset (e.g., pandas DataFrame or list of dicts) with validation metadata.
    error_handling: If columns are missing or the file cannot be read, raise an error. If there are nulls, flag them explicitly before continuing.

  - name: compute_growth
    description: Computes per-period growth for a specific ward and category using the specified growth type.
    input: Dataset, ward string, category string, and growth_type string.
    output: A per-period table (CSV or structured data) containing the result and the formula used for each row.
    error_handling: If multiple wards/categories are requested for aggregation, or if growth_type is missing, refuse the computation and return an error message. If a row is null, output must flag it instead of computing.
