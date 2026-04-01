# skills.md

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates required columns, and reports null counts and affected rows before returning the data.
    input: File path to CSV (string). Expected columns — period, ward, category, budgeted_amount, actual_spend, notes.
    output: Parsed DataFrame with all columns intact. A separate null report listing each null actual_spend row (ward, category, period, reason from notes column) and total null count.
    error_handling: >
      If the file is missing or unreadable, raise an error with the path attempted.
      If any required column is absent, refuse to proceed and list the missing columns.
      If null actual_spend rows are found, print a warning table of those rows (with notes) before returning — never silently skip or fill them.

  - name: compute_growth
    description: Takes a ward, category, and growth type (MoM or YoY), then returns a per-period growth table with the formula shown alongside each result.
    input: Ward name (string), category name (string), growth_type (enum — "MoM" or "YoY"). Receives the pre-loaded DataFrame from load_dataset.
    output: A table with columns — period, actual_spend, previous_period_spend, growth_rate (%), formula_used. Null actual_spend periods are marked as "NULL — not computed" with the reason from notes.
    error_handling: >
      If growth_type is not provided or is invalid, refuse and ask the user to specify "MoM" or "YoY" — never default.
      If the specified ward or category does not exist in the data, refuse and list the valid options.
      If a period has null actual_spend, flag it in the output as "NULL — not computed" and exclude it from growth calculation — never interpolate or fill.
