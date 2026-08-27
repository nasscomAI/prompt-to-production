# skills.md

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates the presence of required columns, and identifies/reports the count and location of null 'actual_spend' values.
    input: File path (string) to the ward budget CSV.
    output: A validated dataset object along with a report of null rows and their corresponding notes.
    error_handling: Refuse processing if mandatory columns are missing; explicitly list null rows found before proceeding.

  - name: compute_growth
    description: Calculates growth (e.g., MoM) for a specific ward and category combination, outputting a table that includes the formula for each row.
    input: Ward name (string), category name (string), growth type (string), and the validated dataset.
    output: A per-period table showing actual spend, growth results, and the formula used.
    error_handling: Refuse if growth-type is not provided; skip calculation for null rows and instead output the flag/reason; refuse any request for all-ward or all-category aggregation.
