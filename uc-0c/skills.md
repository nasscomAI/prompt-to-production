skills:
  - name: load_dataset
    description: Reads the raw CSV ward budget dataset, validates that all required columns are present, and scans/reports any nulls or anomalies before proceeding.
    input: file_path (str path to budget CSV)
    output: A list of dicts containing rows from the CSV, with numbers converted to floats and null values identified.
    error_handling: Raises ValueError if required columns are missing, or FileNotFoundError if the file cannot be accessed.

  - name: compute_growth
    description: Computes period-over-period growth for a specific ward and category, returning a row-by-row table showing periods, actual spend, growth values, and mathematical formulas.
    input: ward (str), category (str), growth_type (str, e.g. 'MoM'), dataset (list of dicts)
    output: A list of dicts with columns [period, ward, category, actual_spend, growth_rate, formula, status].
    error_handling: Refuses calculation and inserts a placeholder/explanation in growth_rate and formula columns if any value in the computation is null or if growth_type is missing.
