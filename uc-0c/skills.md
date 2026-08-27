# skills.md

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates that all required columns are present, and reports the null count and which rows have null actual_spend values before returning the data.
    input: "File path to a CSV file (string). Expected columns: period, ward, category, budgeted_amount, actual_spend, notes."
    output: >
      A validated pandas DataFrame of the CSV contents, plus a printed summary
      listing: total row count, number of null actual_spend rows, and for each
      null row — the period, ward, category, and reason from the notes column.
    error_handling: >
      If the file does not exist, raise FileNotFoundError with the path.
      If any required column (period, ward, category, budgeted_amount, actual_spend, notes) is missing, raise ValueError listing the missing columns.
      If the file is empty or contains zero data rows, raise ValueError explaining that no data was found.

  - name: compute_growth
    description: Takes a ward, category, and growth type (MoM or YoY), filters the dataset, and returns a per-period growth table with the formula shown alongside each result.
    input: >
      ward (string) — exact ward name to filter on.
      category (string) — exact category name to filter on.
      growth_type (string) — one of "MoM" (month-over-month) or "YoY" (year-over-year).
      DataFrame returned by load_dataset.
    output: >
      A pandas DataFrame (and CSV file) with columns: period, actual_spend,
      previous_actual_spend, growth_formula, growth_percentage.
      Rows with null actual_spend are excluded from computation and flagged
      with a note. The first period (or periods lacking a prior comparator)
      shows "N/A" for growth fields.
    error_handling: >
      If growth_type is not "MoM" or "YoY", refuse and prompt the user to specify a valid growth type.
      If the ward or category does not exist in the dataset, raise ValueError listing available wards/categories.
      If all actual_spend values for the selected ward+category are null, refuse computation and report that no valid data exists.
