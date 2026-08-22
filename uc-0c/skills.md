skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates columns, filters by ward and category, and identifies null actual_spend rows alongside their notes.
    input: File path string to ward_budget.csv, target ward string, and target category string.
    output: A structured list of row records filtered for the specific ward and category, plus a log of flagged null entries.
    error_handling: If the file is missing or required columns are absent, raise an error and terminate execution safely.

  - name: compute_growth
    description: Calculates Month-over-Month (MoM) growth rates for the filtered dataset, embedding formulas and handling null values gracefully without calculation errors.
    input: Filtered dataset list and growth_type string ('MoM').
    output: A per-period table containing period, ward, category, actual_spend, growth_rate, formula, and notes.
    error_handling: If actual_spend is null or the previous period spend is zero/null, mark the growth rate as 'NULL_FLAGGED' and explain why.