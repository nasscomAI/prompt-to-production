skills:
  - name: load_dataset
    description: Opens and ingests the raw budget CSV, immediately logging the total null values and identifying which rows are damaged before returning the data.
    input: File path pointing to the raw budget CSV.
    output: A verified dictionary of rows, paired with an explicit validation report summarizing any missing parameters.
    error_handling: Refuses to silently drop null values, instead maintaining their position to be flagged in computational steps.

  - name: compute_growth
    description: Receives specific scoping variables (ward, category, growth_type), filters the rows, and computes period-over-period growth with exposed formulas.
    input: Validated CSV rows, Target Ward, Target Category, and specified Computational Method (like MoM).
    output: A granular row-by-row mapping representing actual spend alongside growth percentages and formulas calculation strings.
    error_handling: Halts and refuses to evaluate if scope is missing, forcing the operator to define boundaries rather than defaulting to grand totals.
