skills:
  - name: load_dataset
    description: Loads the budget CSV, validates required columns, and reports rows with null actual_spend.
    input: input_path string to ward budget CSV file.
    output: Parsed rows plus metadata including null row count and null row identifiers with notes.
    error_handling: Raises a clear error for missing file/columns and refuses processing if required schema is broken.

  - name: compute_growth
    description: Computes period-wise growth for a single ward and category using an explicit growth type.
    input: Parsed rows, ward string, category string, growth_type string (MoM or YoY), output path.
    output: CSV with per-period values, null flags, growth result, and formula text.
    error_handling: Refuses missing or invalid growth_type, refuses empty filters, and marks non-computable rows without silent fallback.
