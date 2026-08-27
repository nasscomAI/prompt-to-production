# skills.md

skills:
  - name: load_dataset
    description: Reads budget CSV, validates essential columns, reports total null count and exactly which rows have nulls before returning the data structure.
    input: File path to a CSV (string).
    output: Parsed list of dictionaries containing CSV records.
    error_handling: Systematically crash and raise FileNotFoundError if the file is unreachable.

  - name: compute_growth
    description: Takes explicitly specified ward, category, and growth_type, explicitly returning a period-by-period table with formulas proven per outcome.
    input: List of parsed rows, exact ward string, exact category string, and growth type string.
    output: List of dictionary records with the computed output fields mapped to final result layout.
    error_handling: Hard refuse with an exit if growth_type is missing or if input assumes multiple wards or categories. When facing incomplete data fields natively mapped as null, outputs a flag record without skipping the output.
