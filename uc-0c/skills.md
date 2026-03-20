skills:
  - name: load_dataset
    description: Reads the Ward Budget CSV and performs a primary scan for null actual_spend rows.
    input: file_path (string).
    output: List of validated record objects; prints counts of identified nulls.
    error_handling: Return error if file is missing or required columns (6 total) do not exist.

  - name: compute_growth
    description: Computes period-over-period financial growth (e.g. MoM) for a slice of data while preserving formulas.
    input: data_list, ward (str), category (str), growth_type (str).
    output: List of results including period, spend, and the explicit math formula.
    error_handling: Refuse computation if current or prior period is NULL; report the reason instead.
