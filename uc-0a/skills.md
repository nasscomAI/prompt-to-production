skills:
  - name: classify_complaint
    description: Classifies one complaint row into the approved category taxonomy and priority scale.
    input: One CSV row as a dictionary with complaint_id and description plus any supporting fields.
    output: A dictionary with complaint_id, category, priority, reason, and flag.
    error_handling: Missing or ambiguous descriptions return category Other, priority Low, a quoted reason, and flag NEEDS_REVIEW.

  - name: batch_classify
    description: Reads an input complaint CSV, applies classify_complaint row by row, and writes a results CSV.
    input: Input CSV path and output CSV path.
    output: A CSV file with columns complaint_id, category, priority, reason, and flag.
    error_handling: Continues processing after row-level failures by writing a fallback Other or NEEDS_REVIEW result instead of crashing.
