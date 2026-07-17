skills:
  - name: load_dataset
    description: Reads the budget CSV, validates required columns, and reports null rows before any growth calculation is attempted.
    input: CSV file path and expected schema.
    output: A validated pandas DataFrame plus a list of null actual_spend rows with their notes.
    error_handling: Refuses and reports missing files, missing columns, or invalid input instead of guessing.

  - name: compute_growth
    description: Takes a single ward, a single category, and an explicit growth type, then returns a per-period table with formula and growth results.
    input: A filtered DataFrame for one ward + one category and a growth type of MoM or YoY.
    output: A CSV-ready per-period table containing period, actual spend, growth percent, formula, and status.
    error_handling: Refuses if the request is broader than one ward and one category, or if the growth type is not explicitly supplied.
