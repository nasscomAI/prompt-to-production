# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single complaint description into specific category, priority, reason, and flag.
    input: String (complaint description).
    output: Object containing category, priority, reason, and flag.
    error_handling: Sets flag to NEEDS_REVIEW and category to Other if the description is genuinely ambiguous.

  - name: batch_classify
    description: Reads an input CSV, applies classify_complaint to each row, and writes the results to an output CSV.
    input: File path to input CSV.
    output: File path to output CSV.
    error_handling: Ensures the output file is generated even if some rows fail, with errors caught per-row.
