skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates required columns, and detects missing values.
    input: File path to the budget CSV document.
    output: A validated dataset, alongside a report of the total null count and exactly which rows contain those nulls.
    error_handling: Refuses to proceed and returns an error if the dataset is missing or malformed.

  - name: compute_growth
    description: Takes a filtered dataset (ward + category) and a required growth_type, returning a per-period table with explicit formulas.
    input: Validated dataset logically scoped to ward and category, and a required growth_type.
    output: A per-period data table explicitly showing the growth value alongside the formula used to calculate it for every row.
    error_handling: Refuses execution if growth_type is unspecified. Flags null rows before computing any metrics.
