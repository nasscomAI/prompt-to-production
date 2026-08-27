# skills.md

skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates the target columns, and explicitly reports the presence and reasons for any null values before proceeding.
    input: Filepath to the CSV (string).
    output: A validated dataset object (list/dataframe) along with a null-report detailing rows with missing data and their notes.
    error_handling: Halts execution if the file is unreadable, missing required schema columns, or if critical dimension columns are entirely empty.

  - name: compute_growth
    description: Computes the specified growth metric for a target ward and target category on a time-series basis, attaching the formula used.
    input: The validated dataset object, target_ward (string), target_category (string), and growth_type (string, e.g., 'MoM').
    output: A structured table containing period, actual_spend, computed_growth, formula_used, and notes (especially for flagged nulls).
    error_handling: Refuses to compute if growth_type is missing. Skips computation for null rows, outputting 'REFUSED: Null Data' and passing through the source note. Refuses if asked to aggregate across unspecified wards/categories.
