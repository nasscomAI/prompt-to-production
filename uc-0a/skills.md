# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint description to output a valid category, determine priority based on explicit severity keywords, cite a justification reason, and set an ambiguity flag if needed.
    input: A single string representing a citizen complaint description.
    output: A structured object containing four fields: category (from exact allowed list), priority (Urgent/Standard/Low), reason (one sentence citation), and flag (NEEDS_REVIEW or blank).
    error_handling: If the complaint description is genuinely ambiguous, assigns category to its closest match or 'Other', and strictly sets the flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV of citizen complaints, iterates over each row calling classify_complaint, and writes all classified outputs to a new results CSV file.
    input: Filepath to the input CSV (e.g., ../data/city-test-files/test_[your-city].csv) and filepath to the target output CSV.
    output: Writes to the target output CSV containing the final results (e.g., uc-0a/results_[your-city].csv). Returns a success status or the total count of processed rows.
    error_handling: If the input file is missing, halts and raises an error. If individual row classifications fail, logs the failure and continues processing the rest of the batch.
