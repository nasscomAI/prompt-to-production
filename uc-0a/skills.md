skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint to assign a category, priority, reason, and an optional review flag.
    input: A single string or data row representing the complaint description.
    output: A structured classification containing category (string), priority (string), reason (string), and flag (string, optional).
    error_handling: If the complaint is ambiguous or invalid, sets category to 'Other' and flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads a batch of complaints from an input CSV, processes each row using classify_complaint, and writes results to an output CSV.
    input: File path to the input CSV containing citizen complaints.
    output: An output CSV file populated with the original data alongside the newly classified category, priority, reason, and flag columns.
    error_handling: If a row is malformed or cannot be processed, it skips the row or logs the error, ensuring the batch continues processing.
