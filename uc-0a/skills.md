skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag using specific taxonomy and rules.
    input: A single row representing a citizen complaint (string description).
    output: A dictionary or object containing category, priority, reason, and flag.
    error_handling: If the category is ambiguous, set category to "Other" and flag to "NEEDS_REVIEW".

  - name: batch_classify
    description: Processes an entire CSV file of complaints, applying classify_complaint to each row and saving the results.
    input: Path to the input CSV file.
    output: Path to the output CSV file containing classified results.
    error_handling: Logs any row-level failures and continues processing the remaining rows.
