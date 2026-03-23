skills:
  - name: classify_complaint
    description: Classifies one complaint row into the approved category and priority schema with a citation-style reason.
    input: A dictionary representing one CSV row with complaint_id, description, location, and other source fields.
    output: A dictionary with complaint_id, category, priority, reason, and flag.
    error_handling: If the description is missing or ambiguous, return category Other, set flag to NEEDS_REVIEW, and explain the failure in reason.

  - name: batch_classify
    description: Reads a complaint CSV, applies classify_complaint to each row, and writes a resilient output CSV.
    input: Input CSV path and output CSV path.
    output: A results CSV containing one output row per input row, even if some source rows are incomplete or malformed.
    error_handling: Never crash the batch on a bad row; preserve complaint_id when available, mark the row NEEDS_REVIEW, and continue processing.
