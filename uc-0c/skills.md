skills:
  - name: load_dataset
    description: >
      Reads the input budget CSV file, validates its column structure,
      counts and logs any rows with null actual_spend values along with their notes.
    input: >
      str (input_path) — path to the input CSV file.
    output: >
      list of dicts — the loaded and parsed rows of the dataset.
    error_handling: >
      Raises FileNotFoundError if the file does not exist.
      Raises ValueError if required columns (period, ward, category, budgeted_amount, actual_spend) are missing.

  - name: compute_growth
    description: >
      Computes the period-over-period growth for a specific ward and category
      under a specified growth type, showing the formula used and flagging nulls.
    input: >
      dataset (list of dicts), ward (str), category (str), growth_type (str).
    output: >
      list of dicts — rows for the specific ward and category, containing period, ward,
      category, actual_spend, growth (percentage or NULL), formula, and notes.
    error_handling: >
      Raises ValueError if growth_type is not provided or invalid.
      Refuses calculation and raises ValueError if ward or category is empty,
      not specified, or requests aggregation (e.g., 'Any', 'All').
