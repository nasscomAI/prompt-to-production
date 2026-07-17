skills:
  - name: classify_complaint
    description: Takes one complaint row and returns a strict category, priority, reason, and flag using the UC-0A schema.
    input: A single complaint row dictionary with a description field.
    output: A dictionary with complaint_id, category, priority, reason, and flag.
    error_handling: If the description is missing or too ambiguous, classify as Other and set flag to NEEDS_REVIEW.

  - name: batch_classify
    description: Reads the source complaint CSV, classifies each row individually, and writes a results CSV with the required fields.
    input: Input CSV path and output CSV path.
    output: A new CSV file containing one row per complaint with category, priority, reason, and flag.
    error_handling: Continues processing even if one row fails, writing a safe fallback row with NEEDS_REVIEW.
