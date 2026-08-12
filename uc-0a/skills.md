skills:
  - name: classify_complaint
    description: Classify one citizen complaint into the fixed UC-0A category and priority taxonomy.
    input: A single complaint description as a string.
    output: A classification containing category, priority, reason, and flag.
    error_handling: If the description is ambiguous or does not map confidently to an allowed category, return category Other and flag NEEDS_REVIEW.

  - name: batch_classify
    description: Read complaint records from a CSV file, classify each complaint, and write the results to a CSV file.
    input: A CSV file containing a description column and an output CSV path.
    output: A CSV containing category, priority, reason, and flag for every input complaint.
    error_handling: Reject missing or invalid input data and preserve NEEDS_REVIEW for genuinely ambiguous complaints.