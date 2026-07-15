# UC-0A Skills

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into the required schema with a validated category, priority, reason, and review flag.
    input: A dictionary-like row from a CSV containing complaint_id and description fields.
    output: A dictionary with complaint_id, category, priority, reason, and flag.
    error_handling: If the description is missing or unclear, return category Other, priority Standard, a brief reason, and flag NEEDS_REVIEW.

  - name: batch_classify
    description: Reads an input CSV, applies classify_complaint to every row, and writes a results CSV with one row per complaint.
    input: A file path to an input CSV and a destination path for the output CSV.
    output: A CSV file containing complaint_id, category, priority, reason, and flag for each input row.
    error_handling: Continue processing rows even if one row is malformed or raises an exception; emit a fallback row with NEEDS_REVIEW.
