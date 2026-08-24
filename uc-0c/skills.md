# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: >
      Read the ward_budget.csv file, validate required columns, and report
      null actual_spend rows before returning the data.
    input: >
      A file path (string) pointing to ward_budget.csv.
    output: >
      A validated dataset (list of row dicts or DataFrame) with columns:
      period, ward, category, budgeted_amount, actual_spend, notes.
      Before returning, prints a null report listing every row where
      actual_spend is blank/null — including period, ward, category, and
      the reason from the notes column.
    error_handling: >
      If the file does not exist, raise a clear error with the path.
      If required columns (period, ward, category, budgeted_amount,
      actual_spend) are missing, refuse to proceed and list the missing
      columns. If no data rows are found, report empty dataset and exit.

  - name: compute_growth
    description: >
      Filter data to a specific ward and category, then compute per-period
      growth rates with the formula shown alongside each result.
    input: >
      The validated dataset, a ward name (string), a category name (string),
      and a growth type (string, e.g. "MoM").
    output: >
      A per-period table (CSV) with columns: period, actual_spend,
      previous_spend, formula, growth_rate, flag. Each row shows the raw
      values and the formula used (e.g. "(19.7 - 14.8) / 14.8 * 100").
      Null periods are marked with flag = NULL and growth_rate = N/A.
    error_handling: >
      If the specified ward or category does not exist in the dataset,
      refuse and list available wards/categories. If growth_type is not
      provided, refuse and ask the user to specify. If a period has null
      actual_spend, mark that row and any adjacent growth calculation as
      N/A with the null reason from the notes column.
