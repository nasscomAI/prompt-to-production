# skills.md

skills:
  - name: load_dataset
    description: Reads CSV file, validates schema, flags null values, and reports data summaries before computation.
    input: file_path (string pointing to CSV at ../data/budget/ward_budget.csv)
    output: |
      {
        "valid": boolean,
        "row_count": int,
        "null_rows": [{"period": "2024-03", "ward": "Ward 2", "category": "Drainage", "reason": "..."}],
        "wards": ["Ward 1 – Kasba", ...],
        "categories": ["Roads & Pothole Repair", ...]
      }
    error_handling: |
      - If CSV has wrong column count: Refuse and report expected vs. actual columns.
      - If actual_spend column is empty or non-numeric: Refuse and report which rows are malformed.
      - If input file not readable: Refuse with file path and permission error.

  - name: compute_growth
    description: Computes growth rate (MoM or YoY) for a specific ward-category pair, showing formula for each row.
    input: ward (string), category (string), growth_type (enum: "MoM" or "YoY")
    output: |
      [
        {"period": "2024-02", "actual_spend": 14.8, "growth_value": null, "growth_formula": "N/A (first period)", "null_reason": null},
        {"period": "2024-07", "actual_spend": 19.7, "growth_value": "+33.1%", "growth_formula": "(19.7 − 14.8) / 14.8", "null_reason": null},
        {"period": "2024-03", "actual_spend": null, "growth_value": null, "growth_formula": "N/A", "null_reason": "Drainage & Flooding: no data"}
      ]
    error_handling: |
      - If growth_type not specified or invalid: Refuse and ask user to choose "MoM" or "YoY".
      - If ward+category pair not found: Refuse and list available combinations.
      - If all periods for that pair are null: Refuse and report "insufficient data".
