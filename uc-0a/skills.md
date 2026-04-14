skills:
  - name: classify_complaint
    description: Classify one complaint row into the required category, priority, reason, and review flag fields.
    input: CSV row as a mapping with complaint_id and description text.
    output: Mapping with complaint_id, category, priority, reason, and flag.
    error_handling: If the description is blank or ambiguous, return category Other with flag NEEDS_REVIEW and explain the uncertainty in the reason.

  - name: batch_classify
    description: Read the complaint CSV, classify each row, and write a complete results CSV without dropping rows.
    input: Input CSV path plus output CSV path.
    output: Results CSV containing one classified row for every input complaint.
    error_handling: If a row is malformed, preserve complaint_id when possible, mark category Other with NEEDS_REVIEW, and continue processing the remaining rows.
