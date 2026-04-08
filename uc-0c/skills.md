skills:
  - name: load_dataset
    description: Load the ward budget dataset and validate its structure.
    input: Path to ward_budget.csv file.
    output: Dataset rows with detected null values and list of affected rows.
    error_handling: If required columns are missing or the file cannot be read, stop execution and return an error.

  - name: compute_growth
    description: Calculate growth metrics for a specific ward and category across periods.
    input: Dataset rows filtered by ward and category plus growth_type (MoM or YoY).
    output: Table of period-wise growth values including formula used and null flags.
    error_handling: If previous value required for growth is missing or null, flag the row and do not compute growth.