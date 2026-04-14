# skills.md — UC-0C Dataset & Computation Skills

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates the schema, and identifies null rows before processing.
    input: File path to ward_budget.csv.
    output: A validated list of records or a DataFrame.
    error_handling:
      - Fail if required columns (period, ward, category, budgeted_amount, actual_spend, notes) are missing.
      - Report a summary of all rows with null 'actual_spend' values and their reasons from the notes column.
      - Stop processing if the dataset structure is corrupted or unreadable.

  - name: compute_growth
    description: Calculates per-period growth for a specific ward and category based on growth_type.
    input: 
      - ward: exact string name
      - category: exact string name
      - growth_type: [MoM, YoY]
      - data: the validated dataset
    output: A per-period table (CSV formatted) with calculated growth and the formula used.
    error_handling:
      - Refuse if ward or category name is "All" or suggests aggregation.
      - If growth_type is missing, return an error requesting clarification.
      - If a row has null 'actual_spend', mark the growth column as 'NULL - [Reason from notes]'.
      - If the previous period's data is missing or null, mark growth as 'N/A - Missing Baseline'.
      - Ensure division by zero (if previous_actual is 0) is handled as a refusal/error with a clear note.