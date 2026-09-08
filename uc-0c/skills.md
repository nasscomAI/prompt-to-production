# skills.md

skills:
  - name: load_dataset
    description: Load the ward budget CSV, validate the required columns, report the number and identity of null actual_spend rows, and return the dataset with notes preserved.
    input: A file path string to the budget CSV and an expected schema containing period, ward, category, budgeted_amount, actual_spend, and notes.
    output: A structured dataset object containing the validated rows, the null row count, and a null-summary list showing which rows are blank in actual_spend and the corresponding note text.
    error_handling: If required columns are missing or the file is unreadable, return a validation error and refuse to compute growth rather than continuing with a partial or guessed dataset.

  - name: compute_growth
    description: Compute a ward-specific and category-specific budget growth table for the requested growth type while showing the formula used and flagging any null actual_spend rows.
    input: A filtered dataset object plus ward, category, and growth_type values provided by the user, such as MoM or YoY.
    output: A per-period CSV/table row list containing ward, category, period, actual_spend, budgeted_amount, growth_percent, formula, and flag or null_reason fields for null rows.
    error_handling: If the requested input is missing a growth type, if all wards or categories are requested instead of a ward-category pair, or if a null actual_spend row would be used for computation, refuse and return an error or mark the row as NEEDS_REVIEW rather than computing silently.
