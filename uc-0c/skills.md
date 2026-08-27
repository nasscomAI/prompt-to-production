# skills.md

skills:
  - name: load_dataset
    description: Reads CSV, validates required columns, reports null count, and lists specific null rows before returning the parsed dataset.
    input: Filepath to CSV (string).
    output: Parsed list of dictionaries containing CSV rows and preprocessing metadata.
    error_handling: Return error if file is missing or if columns do not match expected budget schema.

  - name: compute_growth
    description: Takes specific ward, category, and growth_type constraint, and returns a per-period table showing calculated growth along with the formula.
    input: Parsed dataset, ward (string), category (string), and growth_type (string).
    output: List of calculation dicts to be written into the output CSV.
    error_handling: Refuse computation if growth_type is missing or if an unrequested multi-ward aggregation is invoked.
