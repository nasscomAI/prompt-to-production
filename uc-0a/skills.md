# skills.md - UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies one civic complaint row into the UC-0A category, priority, reason, and review flag schema.
    input: A dictionary representing one CSV row, including complaint_id and description.
    output: A dictionary with complaint_id, category, priority, reason, and flag.
    error_handling: >
      If the description is empty, unclear, or unsupported by the allowed
      categories, return category Other and flag NEEDS_REVIEW. If multiple
      category signals are present, choose a deterministic primary category and
      set flag NEEDS_REVIEW. Always return a one-sentence reason.

  - name: batch_classify
    description: Reads an input complaint CSV, applies classify_complaint to every row, and writes the results CSV.
    input: Input CSV path and output CSV path.
    output: A CSV containing complaint_id, category, priority, reason, and flag columns.
    error_handling: >
      Do not stop the whole batch when one row fails. For unprocessable rows,
      write category Other, priority Standard, a one-sentence reason, and flag
      NEEDS_REVIEW.
