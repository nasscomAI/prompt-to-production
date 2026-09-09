# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates the expected columns, and reports the null count and the specific null rows before returning the dataset.
    input: str — path to the ward_budget.csv file.
    output: tuple — (dataset rows, list of null-row reports) where each report identifies the null actual_spend row and its notes reason.
    error_handling: If the file is missing, a required column (period, ward, category, budgeted_amount, actual_spend, notes) is absent, or the period format is wrong, raises a clear error and returns nothing rather than a partial dataset.

  - name: compute_growth
    description: Computes growth (MoM or YoY) for one specific ward and category and returns a per-period table, with null rows flagged and the formula shown.
    input: str — ward name; str — category name; str — growth type ("MoM" or "YoY"); dataset from load_dataset.
    output: list of rows — per-period growth table with columns for period, actual spend, previous period value, growth value, formula used, and null flag/reason when the period has a null actual_spend.
    error_handling: If the growth type is not MoM or YoY, refuses and asks instead of guessing; if the ward/category is not in the data, returns an explicit error; for null periods, flags them with the notes reason and does not compute a growth value.