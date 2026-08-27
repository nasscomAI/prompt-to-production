skills:
  - name: classify_complaint
    description: Receives one complaint row and outputs the classification category, priority, reason, and flag.
    input: One complaint row text string from the CSV.
    output: A structured object containing category, priority, reason, and flag.
    error_handling: Return flag as NEEDS_REVIEW when the category is genuinely ambiguous or has false confidence.

  - name: batch_classify
    description: Reads the input CSV, applies classify_complaint per row, and writes the output CSV.
    input: Path to the input CSV file.
    output: Writes the results to the output CSV file.
    error_handling: In cases of severe malformation, log the error for that row and continue processing the rest.
