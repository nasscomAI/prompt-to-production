skills:
  - name: load_dataset
    description: >
      Reads a ward budget CSV file, validates required columns, identifies and reports
      any rows containing null/blank actual spend values with their notes before returning.
    input: >
      file_path (string): Path to the budget CSV file.
    output: >
      pandas.DataFrame containing columns: period, ward, category, budgeted_amount, actual_spend, notes.
    error_handling: >
      If file is missing or invalid CSV, raise FileNotFoundError or ValueError.
      If required columns (period, ward, category, budgeted_amount, actual_spend, notes) are missing,
      raise ValueError. Reports null rows explicitly to the log/console.

  - name: compute_growth
    description: >
      Computes MoM or YoY growth for a specific ward and category, returning a per-period
      table showing the actual spend, growth value, growth formula used, and notes.
    input: >
      df (pandas.DataFrame): The validated budget dataset.
      ward (string): Target ward name.
      category (string): Target category name.
      growth_type (string): 'MoM' or 'YoY'.
    output: >
      pandas.DataFrame containing per-period rows for the target ward and category,
      with columns: period, ward, category, budgeted_amount, actual_spend, growth, formula, notes.
    error_handling: >
      If growth_type is invalid or missing, raise ValueError.
      If the specified ward or category does not exist in the dataset, raise ValueError.
      If actual spend is null for either current or reference period, or if the reference
      period does not exist, growth is set to NULL, and the reason is recorded in the notes column.
