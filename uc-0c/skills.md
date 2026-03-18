# skills.md - UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: >
      Reads the ward budget CSV, validates that all required columns are present,
      reports the total null count and the specific rows with null actual_spend
      values before returning the dataset.
    input: >
      A string: file_path - the path to the ward_budget.csv file.
    output: >
      A dict with keys:
        - data        (list of dicts) - all rows from the CSV, unmodified
        - null_rows   (list of dicts) - rows where actual_spend is null/blank,
                      each including period, ward, category, notes
        - null_count  (int)           - total number of null actual_spend rows
      Raises FileNotFoundError if the file cannot be read.
      Raises ValueError if any required column is missing.
    error_handling: >
      If the file is missing, raise FileNotFoundError with the file path.
      If required columns (period, ward, category, budgeted_amount,
      actual_spend, notes) are absent, raise ValueError listing the missing
      columns. Never return data without first reporting null_rows and
      null_count - the null report is mandatory, not optional.

  - name: compute_growth
    description: >
      Takes a ward, category, and growth_type, filters the dataset to that
      ward and category, and returns a per-period table with the growth
      formula, input values, and computed result shown for each row.
    input: >
      Four arguments:
        - data        (list of dicts) - as returned by load_dataset
        - ward        (str)           - exact ward name to filter on
        - category    (str)           - exact category name to filter on
        - growth_type (str)           - must be exactly "MoM" or "YoY"
    output: >
      A list of dicts, one per period in chronological order, each with keys:
        - period       (str)   - e.g. "2024-07"
        - actual_spend (float or None)
        - growth       (float or None) - percentage, 2 decimal places
        - formula      (str)   - human-readable formula with values substituted,
                                 e.g. "((19.7 - 14.8) / 14.8) * 100"
        - status       (str)   - "OK", "NOT COMPUTED - null actual_spend",
                                 or "NOT COMPUTED - no prior period"
    error_handling: >
      If growth_type is not "MoM" or "YoY", raise ValueError:
      "Growth type not specified. Please provide --growth-type MoM or
      --growth-type YoY." Never default silently.
      If the ward or category combination returns zero rows, raise ValueError
      listing the ward and category so the caller can correct the input.
      If a row has null actual_spend, set growth=None, formula="N/A", and
      status="NOT COMPUTED - null actual_spend". Never skip the row.
