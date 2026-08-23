# skills.md

skills:
  - name: load_dataset
    description: >
      Reads the ward budget CSV, validates required columns exist, reports the count
      of null actual_spend values and which rows (period, ward, category) are affected
      before returning the DataFrame.
    input: >
      A file path (string) to a CSV with columns: period, ward, category,
      budgeted_amount, actual_spend, notes.
    output: >
      A pandas DataFrame with validated columns plus a printed summary of null rows.
    error_handling: >
      If the file is missing, columns are missing, or the CSV cannot be parsed, raise
      a clear error message. Do not silently proceed with partial data.

  - name: compute_growth
    description: >
      Computes growth (MoM or YoY) for a given ward and category, returning a
      per-period table with the formula and both numerator/denominator values shown.
    input: >
      A DataFrame from load_dataset, a ward name (string), a category name (string),
      and a growth_type (string, one of "MoM" or "YoY").
    output: >
      A DataFrame with one row per period containing: period, actual_spend,
      previous_spend, growth_value, growth_type, formula. Rows with null actual_spend
      are flagged with the null reason instead of a computed value.
    error_handling: >
      If growth_type is not "MoM" or "YoY", raise an error. If ward or category do
      not exist in the data, raise an error listing valid values. If the DataFrame
      has null actual_spend rows not yet reported, flag them before computing.
