skills:
  - name: classify_complaint
    description: Classify one citizen complaint into an allowed category, priority, evidence-based reason, and review flag.
    input: A dictionary containing complaint_id and description from one CSV row.
    output: A dictionary containing complaint_id, category, priority, reason, and flag.
    error_handling: If the description is missing or invalid, return category Other, priority Standard, a one-sentence reason, and flag NEEDS_REVIEW.

  - name: batch_classify
    description: Read the complete complaint CSV, classify each row independently, and write the results to an output CSV.
    input: Input CSV path and output CSV path.
    output: CSV containing complaint_id, category, priority, reason, and flag for every input row.
    error_handling: Do not crash on a bad row; produce a result for that row with flag NEEDS_REVIEW and continue processing the remaining rows.