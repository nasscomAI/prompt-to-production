skills:
  - name: classify_complaint
    description: Classifies a citizen complaint into category, priority, reason and flag.
    input: Complaint description from CSV file.
    output: category, priority, reason, flag.
    error_handling: If the complaint is ambiguous set flag to NEEDS_REVIEW.

  - name: batch_classify
    description: Reads a CSV file and applies classify_complaint to each complaint.
    input: CSV file containing complaint descriptions.
    output: CSV file with classification results.
    error_handling: Skip invalid rows and mark them for review.
