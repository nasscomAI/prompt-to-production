# UC-0C Budget Growth Skills

skills:
  - name: load_dataset
    description: Read the budget CSV, validate required columns, and report the rows with missing actual_spend values.
    input: A file path to the budget CSV.
    output: A list of row dictionaries plus any null-row details for review.
    error_handling: Stop with a clear error if the required columns are missing.

  - name: compute_growth
    description: Compute per-period growth for one ward and one category using the requested growth type.
    input: The dataset rows, a ward name, a category name, and a growth type.
    output: A CSV-ready list of rows containing period, actual spend, growth percentage, formula, and null status.
    error_handling: Flag null months and refuse to aggregate across multiple wards or categories.
