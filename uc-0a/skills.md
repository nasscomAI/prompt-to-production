skills:
  - name: classify_complaint
    description: Analyzes one citizen complaint row and determines its standardized classification.
    input: Text description of a single civic issue from the CSV row.
    output: A standardized record yielding exactly four fields (category, priority, reason, flag).
    error_handling: Set category to 'Other' and flag to 'NEEDS_REVIEW' if the input description is incomprehensible or missing.

  - name: batch_classify
    description: Reads an input CSV file of multiple complaints, iterates through them applying classify_complaint, and writes the results to an output CSV.
    input: Path to the input CSV file.
    output: Path to the successfully written output CSV containing the classification columns.
    error_handling: Logs the error and halts if the file cannot be found; skips the row and logs an error if an individual line cannot be parsed.
