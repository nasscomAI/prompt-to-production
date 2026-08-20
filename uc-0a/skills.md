# skills.md - UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies one municipal complaint row into the exact UC-0A category and priority schema.
    input: A dictionary containing at least complaint_id and description fields from a CSV row.
    output: A dictionary with complaint_id, category, priority, reason, and flag.
    error_handling: Missing or empty descriptions return category Other, priority Low, a one-sentence reason, and flag NEEDS_REVIEW.

  - name: batch_classify
    description: Reads an input complaint CSV, applies classify_complaint to every row, and writes a results CSV.
    input: Input CSV path and output CSV path as strings.
    output: A CSV file with header complaint_id, category, priority, reason, flag and one output row for every input row.
    error_handling: Malformed rows are written as Other, Low, NEEDS_REVIEW rows so the batch still completes.
