skills:
  - name: load_dataset
    description: Read the budget CSV, validate required columns, and report null rows before returning the filtered data.
    input: "Path to a CSV file containing period, ward, category, budgeted_amount, actual_spend, and notes columns."
    output: "A validated row list with null-reporting metadata and the original dataset values ready for numerical analysis."
    error_handling: "If required columns are missing, raise a clear validation error and stop before calculation; if null actual_spend values exist, keep them flagged without dropping them from the result set."

  - name: compute_growth
    description: Compute a period-over-period growth value for one ward and one category, showing the formula used for each row.
    input: "A filtered dataset for one ward and one category, plus an explicit growth type such as MoM or YoY."
    output: "A CSV-ready list of rows including period, actual spend, growth percentage, formula, and null flags."
    error_handling: "If the growth type is unspecified or the scope spans more than one ward/category, refuse and ask for the required explicit parameters instead of guessing."
