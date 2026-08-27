# skills.md

skills:
  - name: load_dataset
    description: Reads the input budget CSV file, validates expected column headers, and counts/identifies rows with null actual spend.
    input: file_path (string) - Absolute or relative path to the ward budget CSV file.
    output: dataset (list of dicts) - List of rows, where each row maps column names to values, with null values preserved.
    error_handling: Raises FileNotFoundError if the file is missing, and ValueError if required columns (period, ward, category, budgeted_amount, actual_spend) are missing.

  - name: compute_growth
    description: Filters budget dataset by ward and category, and calculates month-over-month (MoM) growth showing the formula for each period.
    input: dataset (list of dicts) - The validated budget dataset; ward (string) - Ward name; category (string) - Category name; growth_type (string) - Type of growth (e.g. 'MoM').
    output: growth_table (list of dicts) - Periodic breakdown containing ward, category, period, actual_spend, growth_rate, and formula used.
    error_handling: Raises ValueError if growth_type is missing/invalid, or if ward/category does not exist. Flags and reports null rows without calculating growth for those periods.
