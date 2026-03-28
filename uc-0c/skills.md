# skills.md

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates columns, and explicitly reports any null rows and their reasons before passing the data to computation.
    input: CSV file path.
    output: Cleaned list of dictionaries with noted null anomaly instances.
    error_handling: Refuse execution if mandatory columns are severely malformed.

  - name: compute_growth
    description: Takes specific ward, category, and growth_type to compute period-over-period growth.
    input: Filtered dataset, ward name, category name, growth type (e.g. MoM).
    output: A generated CSV report with computed growth percentages, flags for nulls, and explicit formulas used.
    error_handling: Refuse and throw an error if ward, category, or growth_type are omitted. Do not aggregate across segments.
