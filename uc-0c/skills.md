# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates required columns, and reports the count and identity of NULL actual_spend rows before returning.
    input: String file path to the ward_budget.csv file.
    output: List of row dictionaries with all columns present; prints a NULL report to stdout before returning.
    error_handling: Exits with a clear error if the file is missing or required columns (period, ward, category, actual_spend, notes) are absent.

  - name: compute_growth
    description: Takes a filtered ward + category dataset and growth type, and returns a per-period table with the formula shown alongside each result.
    input: List of row dicts filtered to a single ward and category, plus a growth_type string (MoM or YoY).
    output: CSV rows with columns: period, actual_spend, previous_spend, growth_pct, formula, null_flag.
    error_handling: Marks any row with NULL actual_spend as null_flag=TRUE and skips growth computation for that row; refuses if growth_type is not MoM or YoY.
