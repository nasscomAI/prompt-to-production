# skills.md
# UC-0A Complaint Classifier skills definitions.

skills:
  - name: classify_complaint
    description: Classify a single citizen complaint row into category, priority, reason, and review flag.
    input: A dict containing complaint fields including complaint_id and description.
    output: A dict with keys complaint_id, category, priority, reason, flag.
    error_handling: If description is missing, ambiguous, or invalid, return category Other, priority Standard, flag NEEDS_REVIEW, and a reason explaining the issue.

  - name: batch_classify
    description: Read a complaint CSV, apply classify_complaint to every row, and write a normalized output CSV.
    input: input_path string for the source CSV and output_path string for the target CSV.
    output: A CSV file with header complaint_id, category, priority, reason, flag.
    error_handling: Continue processing when a row fails; write a fallback output row for bad input and flag it as NEEDS_REVIEW.
