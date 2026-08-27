skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates required columns, and identifies null values.
    input: File path to CSV (string)
    output: List of records with validated schema and a report of null rows
    error_handling: Raises error if file missing, columns invalid, or data malformed

  - name: compute_growth
    description: Computes growth (MoM or YoY) for a specific ward and category per period.
    input: 
      - dataset (list of records)
      - ward (string)
      - category (string)
      - growth_type (string: MoM or YoY)
    output: Table of period-wise growth including actual spend, growth value, and formula used
    error_handling: 
      - Refuses if ward/category not found
      - Refuses if growth_type is missing
      - Flags rows with null actual_spend instead of computing