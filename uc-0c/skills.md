# skills.md — UC-0C Skills Definition

skills:
  - name: load_dataset
    description: Reads CSV budget dataset, validates schema columns, detects null actual_spend rows, and returns structured records with null notes flagged.
    input: String input_path (path to CSV file).
    output: List of row dictionaries with validated period, ward, category, budgeted_amount, actual_spend, and notes.
    error_handling: Raises ValueError if required CSV headers are missing; flags rows where actual_spend is blank/null.

  - name: compute_growth
    description: Computes per-ward per-category growth table (MoM/YoY), displaying mathematical formulas in every row and flagging null spend periods.
    input: List of records, ward string, category string, growth_type string (MoM or YoY).
    output: List of result dictionaries containing period, ward, category, actual_spend, growth_value, formula_used, and notes.
    error_handling: Refuses execution if growth_type is missing or if global ward aggregation is requested.

