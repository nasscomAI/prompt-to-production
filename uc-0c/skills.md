# skills.md

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates expected columns, and reports null count and the specific rows lacking actual_spend before progressing.
    input: Filepath to the CSV dataset.
    output: A clean list of dictionaries representing the dataset, with a secondary output or log indicating null row anomalies.
    error_handling: Safely aborts or flags rows if columns are missing. Identifies missing actuals strictly as nulls rather than converting them to zero.

  - name: compute_growth
    description: Takes the requested ward, category, and growth_type, computing the growth per period and appending the exact formula used.
    input: Filtered dataset structure, ward string, category string, and growth_type string.
    output: A sequential tabular output detailing the period, actual spend, and the computed growth displaying both percentage and formula.
    error_handling: Refuses to compute if ward/category/growth_type are omitted. Emits a flagged notice if attempting to compute growth over a null period in the denominator or numerator.
