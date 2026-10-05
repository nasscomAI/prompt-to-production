# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single complaint row based on its description.
    input: A string containing the complaint description.
    output: A JSON object with category, priority, reason, and flag fields.
    error_handling: If ambiguous, return "Other" category and "NEEDS_REVIEW" flag.

  - name: batch_classify
    description: Reads an input CSV, applies classify_complaint per row, and writes an output CSV.
    input: Input CSV path and Output CSV path.
    output: A written CSV file with the added classification columns.
    error_handling: If a row fails to classify, flag it as error and continue processing the rest.
