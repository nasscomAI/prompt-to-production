skills:
  - name: classify_complaint
    description: Classifies a single complaint row to determine its exact category, priority, reason, and ambiguity flag.
    input: A single row of complaint data (text/string).
    output: A structured object or row containing 'category', 'priority', 'reason', and 'flag' fields.
    error_handling: If the complaint text is genuinely ambiguous, set the flag to 'NEEDS_REVIEW' and assign the closest category or 'Other'.

  - name: batch_classify
    description: Reads an input CSV containing multiple complaints, applies the classify_complaint skill to each row, and writes the fully classified output to a new CSV file.
    input: An input CSV file path (e.g., test_[city].csv).
    output: An output CSV file path (e.g., results_[city].csv).
    error_handling: Skip or log gracefully if a row is malformed, ensuring that the rest of the CSV is successfully classified and written.
