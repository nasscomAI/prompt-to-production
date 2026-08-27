skills:
  - name: load_dataset
    description: Reads the CSV data, validates columns, and reports the null count and which rows have nulls before returning the dataset.
    input: Filepath to the CSV file (string).
    output: Validated dataset and a summary of null rows.
    error_handling: Halts execution and reports an error if the file is missing or columns do not match the expected structure.

  - name: compute_growth
    description: Computes the specified growth metric for a specific ward and category, returning a per-period table with formulas.
    input: Dataset, ward (string), category (string), and growth_type (string).
    output: A per-period table showing Actual Spend, Growth, and the Formula used for each row.
    error_handling: Refuses and asks for clarification if growth_type is missing; flags null actual_spend rows without computing growth for them.
