# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates columns, and reports null count and which rows have null actual_spend before returning the data.
    input: >
      A file path to the ward_budget.csv file.
    output: >
      A list of row dictionaries with validated columns (period, ward, category,
      budgeted_amount, actual_spend, notes). Also prints a null report listing
      every row where actual_spend is blank, including the period, ward,
      category, and reason from the notes column.
    error_handling: >
      If the file is missing or columns are invalid, raise an error with details.
      If unexpected null values are found beyond the known 5, warn but continue.

  - name: compute_growth
    description: Takes a ward, category, and growth type, filters the dataset, and returns a per-period growth table with the formula shown alongside each result.
    input: >
      ward (string), category (string), growth_type (MoM or YoY), and the
      loaded dataset from load_dataset.
    output: >
      A CSV table with columns: period, actual_spend, previous_spend,
      growth_rate_pct, formula, flag. Each row shows the formula used
      (e.g. "(19.7 - 14.8) / 14.8 × 100 = 33.1%"). Null rows are flagged
      with reason. First period has growth_rate "N/A (first period)".
    error_handling: >
      If growth_type is YoY and only one year of data exists, refuse and
      explain why. If ward or category not found in data, refuse with list
      of valid values. If growth_type is not specified, refuse and ask.
