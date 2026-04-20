# skills.md — UC-0C Budget Growth Calculator

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates required columns, reports null count and identifies which specific rows have null actual_spend values before returning the data.
    input: File path to a CSV file with columns (period, ward, category, budgeted_amount, actual_spend, notes).
    output: Validated DataFrame along with a null report listing each null row's period, ward, category, and reason from the notes column.
    error_handling: If the file is missing or required columns are absent, return an error and halt. If null actual_spend values are found, report all nulls with their notes before proceeding — never silently drop or fill them.

  - name: compute_growth
    description: Takes a specific ward, category, and growth type (MoM or YoY), filters the dataset, excludes null rows, and returns a per-period table with the growth percentage and the formula used for each row.
    input: Ward name (string), category name (string), growth type ('MoM' or 'YoY'), and the validated dataset from load_dataset.
    output: Per-period table with columns (period, actual_spend, previous_value, growth_pct, formula_used, is_null_flag). Null periods are included as flagged rows with no computed growth.
    error_handling: If ward or category does not exist in the dataset, return an error listing valid options. If growth type is not 'MoM' or 'YoY', refuse and ask the user to specify. If a period is null, flag it and skip the computation for that row and any row that depends on it as a baseline.
