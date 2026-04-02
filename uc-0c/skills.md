# skills.md

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates its structure, and identifies all rows with null actual_spend values.
    input: Path to the ward budget CSV file.
    output: A list of dictionaries representing the dataset.
    error_handling: Reports the count of null rows and their reasons before returning.

  - name: compute_growth
    description: Computes month-over-month (MoM) growth for a filtered dataset (ward + category) and includes the formula.
    input: Filtered dataset (list of dicts), growth_type (e.g., MoM).
    output: A list of results containing period, actual_spend, growth_rate, and formula.
    error_handling: Flags null rows as 'NULL' and skips growth calculation for them, quoting the notes reason.
