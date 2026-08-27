# skills.md

skills:
  - name: load_dataset
    description: Read ward_budget.csv and validate column structure and null cells.
    input: Path to CSV file.
    output: List of row dicts, with flagged null actual_spend.
    error_handling: If required columns missing, raise ValueError; if all rows null for query, include warning.

  - name: compute_growth
    description: Compute MoM growth for a specific ward + category, with null row flags.
    input: rows list, ward string, category string, growth_type string (MoM or YoY).
    output: rows with period, actual_spend, prev_spend, growth_pct, formula, note.
    error_handling: If row has null actual_spend, set growth_pct to None and note to "NULL in source"; if ward/category not found, raise ValueError.

