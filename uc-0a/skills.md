# skills.md
skills:
  - name: classify_complaint
    description: Analyzes a single complaint row to extract and classify the exact category, priority, reason, and flag.
    input: "String format containing the raw complaint description from a single CSV row."
    output: "A structured format containing exactly four values: category, priority, reason, flag."
    error_handling: "If ambiguous, sets flag to 'NEEDS_REVIEW'."

  - name: batch_classify
    description: Reads an input CSV file of citizen complaints, applies the classify_complaint skill to each row, and writes the results to an output CSV.
    input: "A file path pointing to an input CSV containing complaints."
    output: "A new CSV file containing the classified results, saved to the local filesystem."
    error_handling: "If the file is not found or malformed, it stops and reports the file-level error."
