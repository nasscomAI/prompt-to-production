# skills.md

skills:
  - name: load_dataset
    description: >
      Reads the ward_budget.csv file, validates that all required columns
      (period, ward, category, budgeted_amount, actual_spend, notes) are
      present, and reports the null count and exactly which rows have null
      actual_spend before returning the DataFrame.
    input: >
      File path to a CSV (string). Expected columns: period (YYYY-MM),
      ward (string), category (string), budgeted_amount (float),
      actual_spend (float or blank), notes (string).
    output: >
      A validated DataFrame plus a null report listing each null row's
      ward, category, period, and reason from the notes column.
      Example null report entry:
        - 2024-03 · Ward 2 – Shivajinagar · Drainage & Flooding · "Pending audit clearance"
    error_handling: >
      If any required column is missing, raise an error and list the
      missing columns. If the file path is invalid or the file is empty,
      raise a descriptive error. Never silently ignore nulls — always
      surface them in the null report before returning.

  - name: compute_growth
    description: >
      Takes a specific ward, category, and growth type (MoM or YoY),
      filters the dataset, and returns a per-period growth table with
      the formula shown alongside every computed value.
    input: >
      ward (string) — exact ward name, e.g. "Ward 1 – Kasba".
      category (string) — exact category name, e.g. "Roads & Pothole Repair".
      growth_type (string) — "MoM" (month-over-month) or "YoY" (year-over-year).
      DataFrame — the validated dataset returned by load_dataset.
    output: >
      A table (DataFrame / CSV) with columns: ward, category, period,
      actual_spend, growth_rate (%), formula_used.
      Null actual_spend rows appear in the table with growth_rate = "NULL"
      and formula_used = "Skipped — null actual_spend: <reason from notes>".
      Example row:
        Ward 1 – Kasba | Roads & Pothole Repair | 2024-07 | 19.7 | +33.1% | (19.7 − 14.8) / 14.8 × 100
    error_handling: >
      If growth_type is not provided or is not one of "MoM"/"YoY", refuse
      and ask the user to specify. If the ward or category does not exist
      in the dataset, raise an error listing available wards/categories.
      If all rows for the given ward+category have null actual_spend,
      refuse computation and report that no valid data exists.
