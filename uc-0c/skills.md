skills:
  - name: load_dataset
    description: Reads a CSV file, validates columns, and explicitly reports the count and location of null rows before returning the data.
    input: File path to the budget CSV dataset.
    output: Parsed dataset along with a pre-computation summary of nulls and their reasons.
    error_handling: If required columns are missing, return a schema error. Do not silently impute or drop nulls; they must be surfaced.

  - name: compute_growth
    description: Computes growth for a specific ward and category, returning a per-period table that includes the explicit formula used.
    input: Ward name, category name, and explicit growth_type (e.g., MoM, YoY).
    output: A per-period table (CSV format) showing actual spend, computed growth, and the formula.
    error_handling: Refuse to compute if growth_type is missing or if requested to aggregate across wards/categories. For null actual_spend rows, skip computation, output NULL, and include the reason.
