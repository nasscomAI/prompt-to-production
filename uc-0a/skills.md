skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint into the correct category, priority, reason, and review flag.
    input: One complaint description as a string.
    output: Category, priority, reason, and flag.
    error_handling: If the complaint is ambiguous, assign category as Other, set flag to NEEDS_REVIEW, and provide a reason.

  - name: batch_classify
    description: Reads the input CSV, classifies every complaint, and writes the results to an output CSV.
    input: Input CSV file containing complaint descriptions.
    output: Output CSV containing category, priority, reason, and flag for each complaint.
    error_handling: Skip invalid rows, continue processing remaining records, and report any processing errors.