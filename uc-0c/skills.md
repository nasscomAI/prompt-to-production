# skills.md

skills:
  - name: load_dataset
    description: >
      Reads the ward budget CSV, validates the required columns, identifies
      every null actual_spend value, and reports the affected rows and their
      notes before returning the dataset.
    input: >
      A path to a CSV file containing period, ward, category, budgeted_amount,
      actual_spend, and notes columns.
    output: >
      A validated collection of budget records together with the total null
      actual_spend count and the affected rows with their notes.
    error_handling: >
      If the file cannot be read, required columns are missing, or the dataset
      is malformed, report an explicit error and stop. Never silently repair
      missing or invalid values.

  - name: compute_growth
    description: >
      Computes growth for exactly one ward and one category using the explicitly
      requested growth type and returns a per-period table with the formula
      shown for every computed row.
    input: >
      A validated dataset, one ward, one category, and an explicitly specified
      growth type such as MoM.
    output: >
      A per-period table containing the ward, category, period, actual_spend,
      formula, growth result, and any null or unavailable-growth reason.
    error_handling: >
      If the ward, category, or growth type is missing or ambiguous, refuse
      instead of guessing. If the current or previous actual_spend is null,
      flag the row and do not compute growth.
