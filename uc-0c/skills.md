# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: >
      Reads the ward_budget.csv file, validates that required columns are
      present, and scans for null actual_spend values. Reports all null
      rows with their period, ward, category, and reason from the notes
      column BEFORE returning the dataset for computation.
    input: >
      A file path (string) pointing to the budget CSV file.
    output: >
      A tuple containing:
        - data (list[dict]): all rows from the CSV as dictionaries
        - null_report (list[dict]): list of null rows with keys:
            period, ward, category, notes (reason for null)
      Also prints the null report to stdout before returning.
    error_handling: >
      If the file is missing or unreadable, print an error and exit.
      If required columns (period, ward, category, budgeted_amount,
      actual_spend) are missing, print an error listing missing columns
      and exit.

  - name: compute_growth
    description: >
      Takes a ward + category + growth_type, filters the dataset to that
      ward-category combination, sorts by period, and computes period-over-period
      growth. For MoM: growth = (current - previous) / previous * 100.
      Shows the formula alongside every result. Flags null rows and
      adjacent-to-null rows as not computable.
    input: >
      - data (list[dict]): the full dataset from load_dataset
      - ward (str): exact ward name to filter
      - category (str): exact category name to filter
      - growth_type (str): "MoM" or "YoY"
      - output_path (str): path to write the output CSV
    output: >
      A CSV file with columns: period, ward, category, actual_spend,
      previous_spend, growth_pct, formula, flag, notes.
      - Normal rows: growth_pct computed, formula shown
      - Null rows: flag = "NULL_DATA", notes = reason from source
      - First row: flag = "NO_PREVIOUS", no growth computed
      - Adjacent to null: flag = "ADJACENT_NULL", growth not computed
    error_handling: >
      If ward or category doesn't match any data, print an error listing
      available wards and categories and exit.
      If growth_type is not "MoM" or "YoY", refuse and ask the user.
