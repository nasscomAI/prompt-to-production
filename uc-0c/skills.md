skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates the expected columns, and identifies and logs all null actual_spend rows.
    input: File path of the budget CSV file.
    output: A list of dicts representing valid rows, or structures ready for computation.
    error_handling: Reports null counts and reasons before proceeding; exits if the file is invalid.

  - name: compute_growth
    description: Performs MoM growth calculations for a specific ward and category, returning a per-period table with formulas.
    input: Filtered rows, target ward, target category, and growth type (MoM).
    output: List of rows containing calculated growth percentages and formula strings.
    error_handling: Returns NULL and outputs the notes warning if a null actual_spend is encountered in current or previous periods. Refuses execution if arguments are missing or invalid.
