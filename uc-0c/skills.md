# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates expected columns, and flags any null actual_spend rows mapped to their reasons prior to analysis.
    input: Filepath string pointing to the CSV (e.g., ward_budget.csv).
    output: Validated dataset structure paired with a report highlighting all null rows and their reason from the notes column.
    error_handling: Refuses execution if file is missing, if expected columns (period, ward, category, budgeted_amount, actual_spend, notes) are missing, or if file fails to load.

  - name: compute_growth
    description: Computes period-over-period growth for a specific ward and category, returning an unaggregated tabular result demonstrating the formula used.
    input: Validated dataset, specific ward string, specific category string, and an explicit growth_type.
    output: A per-ward, per-category growth table where every row shows the original `actual_spend`, the calculated growth result, and the exact formula applied.
    error_handling: Refuses calculation and asks the user if --growth-type is absent. Immediately refuses if asked to aggregate across unstated wards or categories. Outputs null rows intact formatted with their explanation.
