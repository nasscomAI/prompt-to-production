skills:
  - name: load_dataset
    description: >
      Reads the ward_budget.csv file, validates expected columns, and performs a mandatory null scan on actual_spend before returning the data.
    input: >
      File path to the input CSV (e.g., ../data/budget/ward_budget.csv). Expected columns: period, ward, category, budgeted_amount, actual_spend, notes.
    output: >
      A parsed dataset with all 300 rows preserved. Includes a null_report listing every row where actual_spend is null — each entry contains period, ward, category, and the reason extracted from the notes column. Returns null_count as an integer.
    error_handling:
      - "Abort if the file cannot be read or does not exist."
      - "Abort if any expected column (period, ward, category, budgeted_amount, actual_spend, notes) is missing."
      - "Never silently drop or fill null actual_spend values — every null must appear in the null_report with its notes reason."
      - "Abort if null_count is returned as zero when nulls actually exist in the data."

  - name: compute_growth
    description: >
      Computes per-period growth for a single ward and single category using the specified growth type, showing the formula in every output row.
    input: >
      Filtered dataset for exactly one ward and one category. Required parameters: ward (string), category (string), growth_type (MoM or YoY — must be explicitly provided, never assumed).
    output: >
      A per-period table with columns: period, actual_spend, previous_actual_spend, growth_percentage, formula_used. For each computed row, formula_used shows the substituted calculation (e.g., "((19.7 - 14.8) / 14.8) * 100 = 33.1%"). Rows affected by null values are marked as "NULL — not computed" with the null reason from notes.
    error_handling:
      - "Refuse and halt if growth_type is not provided — never default to MoM or YoY."
      - "Refuse if the request spans multiple wards or multiple categories — no cross-ward or cross-category aggregation."
      - "Do not compute growth for any row where actual_spend is null or where the previous period actual_spend is null. Mark as 'NULL — not computed'."
      - "Do not skip or omit null rows from the output table — they must appear with their null flag."
      - "Abort if ward or category provided does not exist in the dataset."
