# skills.md

skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates columns, and reports the null count along with which rows contain nulls before returning the data.
    input: File path to the CSV (string).
    output: Validated dataset (table/dataframe) and a summary report of null rows.
    error_handling: If the file is missing or columns are invalid, raise an error clearly stating the missing components. If nulls are found, flag them before proceeding.

  - name: compute_growth
    description: Takes a dataset filtered by ward and category, along with a specified growth type, and returns a per-period table showing the computed growth and the formula used.
    input: Dataset (table/dataframe), ward (string), category (string), growth_type (string, e.g., 'MoM', 'YoY').
    output: Per-period table (CSV/dataframe) containing original metrics, computed growth, and the exact formula text.
    error_handling: If growth_type is missing or invalid, or if the data contains unhandled nulls, refuse computation and return an error asking for the missing parameter.
