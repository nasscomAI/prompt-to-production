skills:
  - name: classify_complaint
    description: Classifies a single complaint into category, priority, reason, and flag.
    input: A string containing the text of a citizen complaint description.
    output: A JSON object with string fields category, priority, reason, and flag.
    error_handling: If the text is empty or invalid, return category: Other, priority: Low, reason: "Invalid input", flag: NEEDS_REVIEW. If the complaint is genuinely ambiguous, set flag to NEEDS_REVIEW.

  - name: batch_classify
    description: Reads an input CSV, applies classify_complaint to each row, and writes to an output CSV.
    input: File paths for an input CSV and an output CSV.
    output: A populated output CSV file.
    error_handling: If a row fails to process or returns invalid JSON, log the error, leave the classification fields blank or set flag to NEEDS_REVIEW, and continue processing the rest of the rows.
