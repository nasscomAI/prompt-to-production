skills:
  - name: load_dataset
    description: Reads the municipal budget CSV, validates column structure, and pre-identifies every row containing null values in actual_spend.
    input: String representing the absolute path to the budget CSV file.
    output: A collection of validated budget records, including a separate manifest of rows with missing actual_spend data and their corresponding notes.
    error_handling: Refuse processing if mandatory columns (ward, category, period) are missing or if the file cannot be accessed.

  - name: compute_growth
    description: Calculates period-over-period growth for a target ward and category while explicitly documenting the mathematical formula for each row.
    input: Validated budget data (list/dataframe), ward name (string), budget category (string), and growth type (MoM or YoY).
    output: A structured table containing periods, spend, growth percentage, and the explicit formula used (or a null-flag if data is missing).
    error_handling: Explicitly refuse any request for all-ward or all-category aggregations. If growth_type is missing, or if a required comparison period is null, return a descriptive error or flag the row without computing.
