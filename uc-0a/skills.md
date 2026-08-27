# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single complaint description into valid category and priority according to defined schema.
    input: String containing the citizen complaint description.
    output: Dictionary with keys: category (string), priority (string), reason (string), and flag (string).
    error_handling: "If the category is genuinely ambiguous, set category to 'Other' and flag to 'NEEDS_REVIEW'."

  - name: batch_classify
    description: Processes an input CSV file of complaints, classifies each row, and writes the results to an output CSV file.
    input: File path to input CSV (../data/city-test-files/test_[city].csv).
    output: File path to output CSV (uc-0a/results_[city].csv) containing original columns plus category, priority, reason, and flag.
    error_handling: "Skips rows with missing descriptions and logs a warning for any rows that could not be processed."
