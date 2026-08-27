skills:
  - name: load_dataset
    description: Ingests the ward budget CSV and performs a pre-computation audit to identify missing values.
    input: File path to `ward_budget.csv`.
    output: A dataframe/dictionary and a summary of detected NULL rows including their 'notes' content.
    error_handling: If required columns ('ward', 'category', 'actual_spend') are missing, abort and log a structural error.

  - name: compute_growth
    description: Calculates period-by-period growth for a filtered subset of data, embedding the formula in the result.
    input: Ward name, Category name, and Growth-type (e.g., MoM).
    output: A table/list of results containing [Period, Actual Spend, Growth %, Formula, Flag].
    error_handling: If a 'NULL' is encountered in the current or previous period's 'actual_spend', set Growth to 'N/A', Formula to 'Incomplete Data', and Flag to the reason from the notes.