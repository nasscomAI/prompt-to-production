# skills.md

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates the required schema, and reports the null count and which rows are null before any computation.
    input: Path to a CSV with columns period, ward, category, budgeted_amount, actual_spend, notes.
    output: A list of all rows and a list of null actual_spend rows with their period, ward, category, and notes.
    error_handling: Raises FileNotFoundError when the file is missing and ValueError when required columns are absent; never silently skips null rows.

  - name: compute_growth
    description: Computes MoM or YoY growth for one (ward, category) and returns a per-period table that always shows the formula used.
    input: The loaded rows, a single ward, a single category, and an explicit growth_type of MoM or YoY.
    output: A list of rows with period, actual_spend, growth, growth_formula, growth_note, null_flag, and null_reason for every period.
    error_handling: Null actual_spend rows are flagged with their notes reason and never computed; periods with no previous data get an empty growth value with an explanatory growth_note.
