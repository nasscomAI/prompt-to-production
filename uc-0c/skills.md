# skills.md


skills:
  - name: load_dataset
    description: Reads CSV, validates columns, reports null count and which rows before returning.
    input: CSV file path.
    output: A data structure (e.g., pandas DataFrame) with the data, plus a null value report.
    error_handling: Reports errors for file not found, invalid columns, or other read errors.

  - name: compute_growth
    description: Takes ward, category, and growth_type, and returns a per-period table with the formula shown.
    input: Ward (string), Category (string), Growth Type (string).
    output: A per-period table showing the growth calculation and the formula used.
    error_handling: Refuses to guess if growth_type is not specified. Flags nulls instead of computing.
