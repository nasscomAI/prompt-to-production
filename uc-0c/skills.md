# skills.md

skills:

  - name: load_dataset
    description: Reads the budget CSV, validates required columns, and reports null actual_spend rows before returning the data.
    input: Budget CSV file containing ward, category, period, actual_spend, and notes columns.
    output: Loaded rows and a list of null actual_spend rows with their notes.
    error_handling: Reject the dataset when required columns are missing and report every null actual_spend row without crashing.

  - name: compute_growth
    description: Calculates growth for one explicitly requested ward and category using the explicitly requested growth type.
    input: Loaded budget rows, one ward, one category, and growth_type of MoM or YoY.
    output: Per-period growth table containing the result, formula, and status.
    error_handling: Refuse when growth type is missing or invalid, flag null comparison values, and never invent missing values.