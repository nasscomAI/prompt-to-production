# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates required columns are present, and reports the count and details of any null rows found before returning the dataset.
    input: File path to the ward budget CSV (string).
    output: A list of dicts representing the rows of the CSV, each containing period, ward, category, budgeted_amount (float), actual_spend (float or None), and notes (string).
    error_handling: Raises FileNotFoundError if the file doesn't exist. If required columns are missing, raises a ValueError. If a row has non-numeric values for budgeted_amount or actual_spend (other than empty fields), flags a warning but processes the row.

  - name: compute_growth
    description: Computes the growth percentage (MoM) of the actual spend for a specific ward and category over time, and returns a table showing the period, actual spend, growth value, and the calculation formula used.
    input:
      dataset: List of dicts from load_dataset.
      ward: Ward name to filter by (string).
      category: Category to filter by (string).
      growth_type: Growth calculation type, currently only "MoM" is supported (string).
    output: A list of dicts, each representing a row of the filtered data with keys — period, actual_spend, growth_pct, and formula.
    error_handling: Refuses calculation and raises a ValueError if growth_type is not "MoM" or is not specified. Refuses calculation if multiple wards or categories are processed (aggregation is prohibited). If a row contains a null actual_spend, flags the growth as "NULL (Not computed - missing actual spend)" and lists the note. If the previous month is null, growth is flagged as "NULL (Not computed - previous period is null/missing)".
