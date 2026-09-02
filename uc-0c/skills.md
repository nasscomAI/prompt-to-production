skills:
  - name: load_dataset
    description: Reads the budget CSV, validates the required columns, and reports the null rows before returning data for analysis.
    input: A CSV file path to the municipality budget dataset.
    output: A list of validated records with null metadata, including the count and reasons for missing actual_spend values.
    error_handling: If required columns are missing or the file cannot be read, stop with a clear validation error instead of making assumptions.

  - name: compute_growth
    description: Calculates monthly or yearly growth for one ward and one category using the selected growth type, while preserving the exact formula and null flags in each output row.
    input: Filtered records for one ward and one category, plus the requested growth type such as MoM or YoY.
    output: A CSV-ready table with period, previous period, actual spend, growth percentage, formula, and null/flag status for each row.
    error_handling: If the requested ward/category is broad or missing, or if the growth type is not explicitly provided, refuse and ask for clarification rather than guessing.
