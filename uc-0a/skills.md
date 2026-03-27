# skills.md

skills:
  - name: classify_complaint
    description: Processes one citizen complaint row and accurately outputs the designated category, priority, reason, and optional flag.
    input: A single citizen complaint row containing the description text (String).
    output: Structured fields including exactly category (String), priority (String), reason (String), and flag (String).
    error_handling: If the complaint description is genuinely ambiguous, it sets the category as "Other" and the flag as "NEEDS_REVIEW" instead of forcing a confident category classification.

  - name: batch_classify
    description: Reads an input CSV file of citizen complaints, applies the classify_complaint skill iteratively to each row, and writes the structured results to an output CSV.
    input: Path to the input CSV file containing citizen complaints without category and priority_flag (e.g., ../data/city-test-files/test_[your-city].csv).
    output: Path to the output CSV file containing the classified results for each row (e.g., uc-0a/results_[your-city].csv).
    error_handling: Handles malformed rows or exceptions during row processing by skipping or flagging the affected row while ensuring the continued processing of the batch to completely generate the output CSV.
