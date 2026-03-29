skills:
  - name: classify_complaint
    description: Classifies one complaint description into the fixed taxonomy with priority, reason, and optional review flag.
    input: One CSV row as a dictionary containing complaint_id and description fields.
    output: A dictionary with complaint_id, category, priority, reason, and flag.
    error_handling: If the description is blank or ambiguous, return category Other with flag NEEDS_REVIEW instead of guessing.

  - name: batch_classify
    description: Reads the full complaint CSV, applies classify_complaint row by row, and writes the results CSV.
    input: An input CSV path and an output CSV path.
    output: A results CSV with complaint_id, category, priority, reason, and flag for every row.
    error_handling: If one row fails during classification, write Other plus NEEDS_REVIEW for that row and continue processing the file.
