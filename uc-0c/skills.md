# skills.md

skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates the required columns (period, ward, category, budgeted_amount, actual_spend), and reports the count and details (with reason) of any null actual_spend rows.
    input: File path (string) to the ward_budget.csv.
    output: A dataset object containing the validated rows and a separate report of flagged null rows with their notes.
    error_handling: Throws an error if the file is missing, if required columns are absent, or if null rows are found without an accompanying reason in the notes column.

  - name: compute_growth
    description: Calculates growth metrics (e.g., Month-over-Month) for a specific ward and category combination, ensuring no cross-aggregation and explicitly including the calculation formula for each period.
    input: Ward name (string), Category name (string), Growth type (string, e.g., 'MoM'), and the Dataset object.
    output: A per-period growth table mapping to growth_output.csv format, flagging null periods as non-computable and showing the formula used for each result.
    error_handling: Refuses to compute if the growth type is unspecified, if the user asks for multi-ward or multi-category aggregation, or if requested data is missing.
