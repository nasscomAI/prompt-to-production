# skills.md

skills:
  - name: classify_complaint
    description: Classify one citizen complaint into an allowed category and priority, provide a reason, and flag genuine ambiguity.
    input: One complaint row containing a complaint description, provided as a CSV row or structured record.
    output: A classification record containing category, priority, reason, and flag.
    error_handling: If the description is missing or invalid, use category Other and flag NEEDS_REVIEW; if the category is ambiguous, use Other with NEEDS_REVIEW.

  - name: batch_classify
    description: Read a complaint CSV, classify every complaint using classify_complaint, and write the required classification results to an output CSV.
    input: A CSV file containing complaint rows with complaint descriptions.
    output: A CSV file containing complaint_id, category, priority, reason, and flag for every input row.
    error_handling: Reject an unreadable or invalid input CSV with a clear error; continue valid rows and use Other with NEEDS_REVIEW for genuinely ambiguous complaints.