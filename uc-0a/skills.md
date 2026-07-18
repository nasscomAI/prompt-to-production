skills:
  - name: classify_complaint
    description: Classify a single complaint row using keywords and rules to determine category, priority, justification reason, and review flag.
    input: A dictionary containing complaint fields, primarily "description" (string).
    output: A dictionary containing "complaint_id" (string), "category" (string), "priority" (string), "reason" (string), and "flag" (string).
    error_handling: If description is missing, empty, or null, classify category as "Other", priority as "Standard", reason as "No description provided", and set flag to "NEEDS_REVIEW".

  - name: batch_classify
    description: Read an input CSV file containing complaints, classify each complaint, and write the classification results to an output CSV file.
    input: Absolute/relative path to the input CSV file (string) and output CSV file (string).
    output: None (writes results to output CSV file).
    error_handling: Handles missing files gracefully, does not crash on malformed rows, and logs row-level exceptions while continuing process for the rest of the batch.
