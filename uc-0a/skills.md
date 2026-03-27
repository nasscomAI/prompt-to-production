# skills.md

skills:
  - name: classify_complaint
    description: Classifies one complaint row into category, priority, reason, and flag.
    input: One complaint description/row without classification.
    output: Output containing category, priority, reason, and flag.
    error_handling: If genuinely ambiguous, set flag to NEEDS_REVIEW.

  - name: batch_classify
    description: Reads the input CSV, applies classify_complaint per row, and writes the output CSV.
    input: Path to the input CSV file.
    output: Path to the written output CSV file.
    error_handling: Continues processing remaining rows if an error occurs on a specific row.
