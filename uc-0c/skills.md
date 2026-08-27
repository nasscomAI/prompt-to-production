# skills.md - UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates columns, and reports the count and location of any null rows.
    input: File path string to the CSV dataset.
    output: Loaded dataset list/object along with a report of null values and their corresponding notes.
    error_handling: If critical columns are missing or unreadable, halt execution and report the exact missing columns.

  - name: compute_growth
    description: Computes the specified growth metric (e.g. MoM) for a given ward and category, returning a per-period table showing formulas.
    input: Filtered dataset by ward and category, and the required growth_type string.
    output: A structured table containing the computed growth percentages and the explicit formula string used.
    error_handling: If a required actual_spend value is null, flag it, skip the growth computation for that specific period, and include the null reason in the output.
