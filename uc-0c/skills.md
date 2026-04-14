# skills.md

skills:
  - name: load_dataset
    description: Reads the municipal budget CSV, validates required columns, and reports the count and location of null actual_spend rows.
    input: CSV file path (string).
    output: Dataframe containing budget data, and a summary of null rows including reasons from the notes column.
    error_handling: Refuse and report if required columns (period, ward, category, budgeted_amount, actual_spend) are missing.

  - name: compute_growth
    description: Calculates growth metrics (MoM or YoY) for a specific ward and category, including the formula in each row.
    input: ward (string), category (string), growth_type (string: MoM or YoY).
    output: A per-period table for the filtered data with an additional 'formula' column and growth results.
    error_handling: Refuse to compute if growth_type is missing or if the request involves ward/category aggregation. Flag null rows as 'not computed' and include the reason.
