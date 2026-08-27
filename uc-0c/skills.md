skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates columns, and reports null count and which rows contain null values before returning.
    input: Filepath to the CSV dataset (string).
    output: A loaded dataset including a report of any null values found.
    error_handling: Halts and raises an error if the file is missing or lacks the expected columns.

  - name: compute_growth
    description: Takes ward, category, and growth_type to calculate growth and returns a per-period table.
    input: Ward (string), category (string), and growth_type (string).
    output: A per-period table showing the result alongside the formula used in every output row.
    error_handling: Refuses and asks for the missing argument if growth_type is not specified; flags null values without computing them.
