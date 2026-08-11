# skills.md

skills:
  - name: classify_complaint
    description: Classifies one complaint row into a single category, priority, reason, and review flag.
    input: dict with keys complaint_id, description, and complaint metadata.
    output: dict with keys complaint_id, category, priority, reason, flag.
    error_handling: Returns category Other and flag NEEDS_REVIEW when the description is missing or ambiguous.

  - name: batch_classify
    description: Reads an input CSV, applies classify_complaint to each row, and writes an output CSV.
    input: input CSV file path and output CSV file path.
    output: Generated output CSV with complaint_id, category, priority, reason, and flag.
    error_handling: Continues processing on invalid rows, logs errors, and writes NEEDS_REVIEW for failures.
