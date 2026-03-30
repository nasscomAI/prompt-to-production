skills:
  - name: load_dataset
    description: Reads CSV, validates columns, reports null count and which rows before returning.
    input: Filepath to the CSV dataset (string).
    output: Parsed dataset object, a count of null values, and a list of specific rows containing nulls.
    error_handling: Handles missing files or invalid headers by halting and prompting the user. For null values, it flags them with their corresponding reasons from the notes column instead of erroring out.

  - name: compute_growth
    description: Takes ward, category, and growth_type to calculate growth metrics, returning a per-period table with the formula shown.
    input: Dataset object, ward (string), category (string), and growth_type (string, e.g., MoM).
    output: A per-period table containing period, budget, actual spend, the calculated growth value, and the specific formula used for each output row.
    error_handling: If --growth-type is not specified, halts execution and asks the user, never guessing. If actual spend is null for a row, flags the row according to notes and does not attempt computation.
