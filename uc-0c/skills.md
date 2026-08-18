skills:
  - name: load_dataset
    description: Reads the ward_budget CSV, validates required columns are present, and reports the count and details of null actual_spend rows before returning the dataset.
    input: File path to ward_budget.csv.
    output: Tuple of (full dataframe, list of null row details including period, ward, category, and notes). Always prints null report before returning.
    error_handling: If required columns are missing or the file cannot be read, print an error message with column details and exit without computing.

  - name: compute_growth
    description: Takes a specified ward, category, and growth type (MoM or YoY), filters the dataset to that combination, and returns a per-period table with growth rate and formula shown.
    input: Dataframe from load_dataset, ward name (string), category name (string), growth_type (string — must be 'MoM' or 'YoY').
    output: CSV rows containing period, actual_spend, growth_rate (%), formula_used, null_flag. Null rows are included as flagged entries with growth_rate left blank.
    error_handling: If the ward or category is not found in the dataset, return an error listing valid options. If growth_type is not 'MoM' or 'YoY', refuse and prompt the user to specify.
