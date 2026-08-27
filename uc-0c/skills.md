# skills.md

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates requested columns, and reports null counts and affected rows.
    input: File path to the budget CSV.
    output: A validated dataset object/list, along with a report detailing any rows with null actual_spend values and their notes.
    error_handling: Raise an error if the file format is incorrect or essential columns (period, ward, category, budgeted_amount, actual_spend, notes) are missing.

  - name: compute_growth
    description: Takes the validated data for a specific ward and category, along with a growth type, and returns a per-period table showing the expected output.
    input: Validated dataset rows for a specific ward and category, and a required growth_type string (e.g., MoM).
    output: A per-period table (CSV or structured text) containing the growth calculation, indicating formulas used and explicitly flagging nulls.
    error_handling: Refuse execution if growth_type is missing, or if asked to aggregate across multiple wards/categories without explicit instruction.
