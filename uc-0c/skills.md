skills:
  - name: load_dataset
    description: >
      Reads a ward_budget CSV file, validates expected columns exist,
      reports count of null actual_spend rows with their details before
      returning the dataset.
    input: >
      A filesystem path (string) pointing to a CSV file with columns:
      period, ward, category, budgeted_amount, actual_spend, notes.
    output: >
      A dictionary with keys: "rows" (list of dicts), "null_count" (int),
      "null_details" (list of {period, ward, category, reason} for each
      null actual_spend). Returns {"error": "File not found"} if the
      path does not exist, or {"error": "Invalid file"} if columns are
      missing or the file cannot be parsed.
    error_handling: >
      If the file does not exist, return {"error": "File not found"}.
      If required columns are missing, return {"error": "Invalid file:
      missing columns [names]"}. If the file is empty or unreadable,
      return {"error": "Invalid file"}.

  - name: compute_growth
    description: >
      Takes a filtered dataset for one ward and one category, plus a
      growth_type (MoM or YoY), and returns a per-period growth table
      with formula shown.
    input: >
      A list of row dicts (filtered to one ward and one category),
      sorted by period ascending. A growth_type string: "MoM" or "YoY".
    output: >
      A list of dicts, one per period, each containing: period, ward,
      category, budgeted_amount, actual_spend (or NULL), growth_rate
      (formatted string like "+33.1%" or "NULL"), growth_type, formula
      (string like "((2024-07 - 2024-06) / 2024-06) * 100"), and
      null_reason (if actual_spend is NULL). Growth is not computed for
      the first period in the series (or first 12 for YoY) — those rows
      show growth_rate="N/A" with formula="Base period".
    error_handling: >
      If data list is empty, return {"error": "No data for the given
      ward and category."}. If growth_type is not "MoM" or "YoY", return
      {"error": "Invalid growth_type. Use MoM or YoY."}. If fewer rows
      than needed for the requested growth type exist (e.g. YoY needs
      12+ months), return {"error": "Insufficient data for {growth_type}
      calculation. Need at least {n} periods."}.
