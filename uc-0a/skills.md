# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into a category, priority, reason, and flag based on the enforcement rules.
    input: A single complaint row dictionary containing at least a 'description' field.
    output: A dictionary with keys 'category', 'priority', 'reason', and 'flag'.
    error_handling: If the input is missing the 'description', return category: 'Other', priority: 'Low', reason: 'Missing description', flag: 'NEEDS_REVIEW'. If the category is ambiguous, set flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV of citizen complaints, applies the classify_complaint skill to each row, and writes the results to an output CSV.
    input: File paths for the input CSV and the output CSV.
    output: A CSV file written to the output path containing the original columns plus 'category', 'priority', 'reason', and 'flag'.
    error_handling: If a row fails to process or is malformed, log the error, flag nulls if possible, do not crash on bad rows, and ensure an output file is produced for the successful rows.
