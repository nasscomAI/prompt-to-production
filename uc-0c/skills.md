# skills.md

skills:
  - name: load_dataset
    capability: "Read CSV file, validate schema, count and list null rows before returning full dataset."
    resources:
      input_file: "CSV path (string) — e.g., ../data/budget/ward_budget.csv"
      expected_columns: ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
    actions:
      - "Open and parse CSV file"
      - "Validate all 6 columns are present; refuse if missing"
      - "Identify all rows where actual_spend is null or blank"
      - "Report null row count and exact list (period, ward, category, notes reason)"
      - "Return full DataFrame with no rows dropped"
    flow: "Called once at agent startup; blocks further execution if validation fails."
    testing: "✓ Must reject file if columns missing; ✓ Must list all 5 known null rows; ✓ Must not drop or skip null rows."

  - name: compute_growth
    capability: "Calculate MoM or YoY growth for a single ward + category; flag nulls; show formula per row."
    resources:
      dataset: "Loaded DataFrame from load_dataset (must include nulls)"
      ward: "Single ward name (string) — e.g., 'Ward 1 – Kasba'"
      category: "Single category name (string) — e.g., 'Roads & Pothole Repair'"
      growth_type: "Either 'MoM' (month-over-month) or 'YoY' (year-over-year); must be explicit (no default)"
    actions:
      - "Filter dataset to (ward, category) only; refuse if multiple wards or categories requested"
      - "Sort by period ascending (Jan–Dec 2024)"
      - "For each row: if actual_spend is null, flag with notes reason and skip growth calc"
      - "For each non-null row: apply formula (current/prior) − 1 and label as MoM or YoY"
      - "Return table: period, actual_spend, formula_used, growth_value, null_flag, null_reason"
    flow: "Executed after load_dataset; must refuse if growth_type not specified; output fed to growth_output.csv"
    testing: "✓ Must refuse aggregation across wards/categories; ✓ Must flag 5 null rows with reason; ✓ Must show formula for every computed row; ✓ Must reject missing growth_type."
