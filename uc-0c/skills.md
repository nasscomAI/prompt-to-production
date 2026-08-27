# skills.md

skills:
  - name: load_dataset
    description: Reads the CSV dataset, validates columns, and reports null count and their row locations before returning data.
    input: File path to the budget CSV.
    output: Structured dataset object alongside a metadata summary of nulls and their reasons.
    error_handling: If the file is missing columns or unreadable, reject with a schema error and provide instructions. 

  - name: compute_growth
    description: Takes ward, category, and growth_type context to return a per-period table with the computed growth and formula shown.
    input: Filtered dataset by ward and category, plus the explicit growth_type.
    output: Formatted table or CSV data containing period, actual spend, computed growth, formula used, and flags for nulls.
    error_handling: If actual_spend is null for a period, output NULL for the growth and append the reason from the notes column. If growth_type is missing, return an error requesting user clarification.
