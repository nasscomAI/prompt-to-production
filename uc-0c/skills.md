# skills.md

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates required columns, and identifies all rows with null actual_spend.
    input: file_path (Path to CSV)
    output: List of Dictionaries (Valid rows) and List of Null Reports (Null rows + reasons).
    error_handling: Reports error if file is missing or required columns (period, ward, category, actual_spend) are absent.

  - name: compute_growth
    description: Calculates MoM or YoY growth for a specific ward and category based on the loaded dataset.
    input: data (List of rows), ward (String), category (String), growth_type (MoM or YoY)
    output: List of results (Period, Actual Spend, Growth %, Formula, Flag/Reason).
    error_handling: Returns explicit error if growth_type is missing or if input data is insufficient for calculation.
