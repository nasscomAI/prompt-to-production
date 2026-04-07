# skills.md — UC-0C Budget Growth Calculator

skills:
  - name: load_dataset
    description: Reads budget CSV file, validates required columns, identifies and reports null actual_spend values with their reasons before returning the dataset.
    input: |
      - file_path (string) — path to ward_budget.csv file
    output: |
      Dictionary containing:
      {
        "data": [list of row dictionaries with columns: period, ward, category, budgeted_amount, actual_spend, notes],
        "total_rows": int,
        "null_rows": [
          {
            "period": string,
            "ward": string,
            "category": string,
            "reason": string (from notes column)
          }
        ],
        "null_count": int,
        "wards": [list of unique ward names],
        "categories": [list of unique category names],
        "periods": [list of unique periods sorted chronologically]
      }
    error_handling: |
      - If file does not exist → raise FileNotFoundError with clear message
      - If required columns missing (period, ward, category, budgeted_amount, actual_spend, notes) → raise ValueError listing missing columns
      - If CSV is empty or has no data rows → raise ValueError "Dataset contains no data"
      - If null rows detected → ALWAYS report them in output, never silently skip
      - If actual_spend contains non-numeric values (except empty/null) → raise ValueError with row details

  - name: compute_growth
    description: Computes growth rates for a specific ward and category combination, showing formula used for each period, flagging null rows, and refusing to aggregate across wards or categories.
    input: |
      - dataset (dict) — output from load_dataset
      - ward (string) — exact ward name (e.g., "Ward 1 – Kasba")
      - category (string) — exact category name (e.g., "Roads & Pothole Repair")
      - growth_type (string) — either "MoM" (Month-over-Month) or "YoY" (Year-over-Year)
      - output_path (string) — path to write growth_output.csv
    output: |
      CSV file written to output_path with columns:
      - period (string) — YYYY-MM format
      - ward (string) — ward name
      - category (string) — category name
      - actual_spend (float or NULL) — actual spend value in ₹ lakh
      - growth_rate (string) — percentage change with sign (e.g., "+33.1%", "-34.8%") or "N/A" if null
      - formula (string) — formula used (e.g., "(19.7 - 14.8) / 14.8 × 100") or "NULL: <reason>"
      - flag (string) — "NULL_DATA" if current or previous period has null, otherwise empty
    error_handling: |
      - If ward not found in dataset → raise ValueError "Ward '<ward>' not found. Available wards: <list>"
      - If category not found in dataset → raise ValueError "Category '<category>' not found. Available categories: <list>"
      - If growth_type not specified or invalid → raise ValueError "growth_type must be 'MoM' or 'YoY', not guessed"
      - If user requests aggregation across multiple wards (e.g., ward="All") → REFUSE with message "Aggregation across wards is not permitted. Specify a single ward."
      - If user requests aggregation across multiple categories → REFUSE with message "Aggregation across categories is not permitted. Specify a single category."
      - For periods with null actual_spend → set growth_rate="N/A", formula="NULL: <reason from notes>", flag="NULL_DATA"
      - For first period (no previous to compare) → set growth_rate="N/A", formula="First period - no previous data"
      - If output directory does not exist → create it before writing
