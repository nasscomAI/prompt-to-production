# skills.md — UC-0C Budget Growth Calculator

skills:
  - name: load_dataset
    description: Read the budget CSV, validate the expected columns, and report the null actual_spend rows with their reasons before returning the data.
    input: Path to ward_budget.csv.
    output: The parsed rows and a report of the 5 deliberate null actual_spend rows, each with ward, category, period, and the reason from the notes column.
    error_handling: If required columns are missing or the file cannot be read, refuse with a clear error; never proceed on an unvalidated dataset.

  - name: compute_growth
    description: For a given ward, category, and explicit growth type, return a per-period table with the formula shown in every row.
    input: The loaded dataset plus ward, category, and growth_type (MoM or YoY).
    output: A per-period table of growth results, each row showing period, ward, category, result, and the formula string used.
    error_handling: Skip and flag null actual_spend rows instead of imputing; if growth_type is not provided, refuse and ask rather than guessing; if asked to aggregate across wards or categories, refuse.
