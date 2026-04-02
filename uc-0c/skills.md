# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: load_dataset
    description: Load and validate ward budget dataset
    input: file_path
    process:
      - Read CSV file from given path
      - Validate required columns (period, ward, category, budgeted_amount, actual_spend, notes)
      - Identify rows where actual_spend is null
      - Report count and details of null rows
      - Return structured dataset
    output: dataset

  - name: compute_growth
    description: Compute growth values for a specific ward and category
    input: dataset, ward, category, growth_type
    process:
      - Filter dataset by ward and category
      - Sort data by period (month-wise)
      - If growth_type is not provided, refuse to proceed
      - For MoM:
          compute ((current_month - previous_month) / previous_month) * 100
      - Skip computation for rows where actual_spend is null and flag them
      - Include formula used in each row of output
      - Return per-period growth table
    output: growth_table
