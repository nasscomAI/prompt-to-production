# skills.md

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates columns, and reports the count and locations of null 'actual_spend' rows before returning data.
    input: File path to the dataset CSV (string).
    output: A list of validated row dictionaries.
    error_handling: If the file is missing or malformed, halt and return a file parsing error.

  - name: compute_growth
    description: Computes the specified growth metric for a specific ward and category, returning a per-period table with the applied formula.
    input: Validated dataset rows (list), target ward (string), target category (string), and growth_type (string).
    output: A structured table (list of dicts) containing period, actual_spend, growth percentage, and the formula used.
    error_handling: If growth_type, ward, or category is missing, refuse execution. If a row is null, flag it and do not compute growth for that period.
