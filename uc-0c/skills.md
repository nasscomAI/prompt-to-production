# skills.md

skills:
  - name: load_dataset
    description: Reads budget CSV data, validates requisite columns, and reports any null counts and the specific rows lacking data.
    input: File path to the budget CSV.
    output: A validated dataset with a pre-processing report detailing null entries.
    error_handling: Return a structured error citing the missing columns or unreadable rows.

  - name: compute_growth
    description: Computes the specified period growth metrics for a given ward and category.
    input: Dataset, ward name, component category, and growth_type (e.g., MoM, YoY).
    output: A per-period table showing the calculated growth metrics and the explicit formula used.
    error_handling: If growth_type is missing, refuse calculation and return an error asking for the growth type.
