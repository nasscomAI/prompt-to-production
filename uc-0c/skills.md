# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:

  - name: load_dataset
    description: >
      Loads the ward budget CSV file and validates required columns.
      Identifies and reports rows where actual_spend is null.
    input: >
      Path to ward_budget.csv
    output: >
      List of records plus a report of rows with null actual_spend.
    error_handling: >
      If required columns are missing or dataset is malformed,
      return NEEDS_REVIEW.

  - name: compute_growth
    description: >
      Computes growth metrics for a specific ward and category.
      Returns a per-period table including formula and result.
    input: >
      Dataset records, ward name, category name, growth_type.
    output: >
      Structured table with period, actual_spend, growth percentage,
      and formula used.
    error_handling: >
      If actual_spend is null for a period, growth is not computed
      and the row is flagged with the null reason.