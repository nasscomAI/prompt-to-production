# skills.md

skills:
  - name: load_dataset
    description: Reads the CSV dataset, validates expected columns, and identifies deliberate nulls before returning.
    input: File path string to the dataset CSV.
    output: Loaded dataset along with a report of the null count and specific rows containing nulls.
    error_handling: Throws an error or returns a clear message if columns are missing or file is unreadable.

  - name: compute_growth
    description: Calculates growth for a specified ward and category using the designated growth type.
    input: Ward name, category, and growth_type (e.g., MoM) as strings.
    output: A per-period table showing actual spend, computed growth, and the formula used for each row.
    error_handling: Refuses to compute and asks the user if growth_type is missing or if asked to aggregate.
