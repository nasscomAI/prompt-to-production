# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: load_dataset
    description: Read ward budget CSV, validate columns, and report null row details.
    input: string path to invoice data CSV, expected header columns period, ward, category, budgeted_amount, actual_spend, notes.
    output: tuple (rows list, null_rows list) where null_rows contains descriptions of null actual_spend rows.
    error_handling: raise ValueError when columns are missing; parse numeric fields robustly; mark null actual_spend rows and continue.

  - name: compute_growth
    description: Compute per-period growth for a single ward/category and growth type with formula metadata.
    input: rows list, null_rows list, ward string, category string, growth_type string (MoM or YoY).
    output: (output_rows list, flagged list) where each row includes period, actual_spend, growth, formula, notes, status.
    error_handling: if --growth-type missing or invalid, raise ValueError; if ward/category not found, raise ValueError; if actual_spend null insert status NULL_ROW.


