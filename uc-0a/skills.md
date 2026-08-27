# skills.md

skills:
  - name: classify_complaint
    description: Classify a single complaint row into category, priority, reason, and flag.
    input: A dictionary representing one CSV row with keys such as complaint_id, description, location, and other raw complaint fields.
    output: A dictionary with keys complaint_id, category, priority, reason, and flag.
    error_handling: If the description is missing or the row is invalid, return category Other, priority Standard, a reason explaining why classification failed, and flag NEEDS_REVIEW.

  - name: batch_classify
    description: Read a complaint CSV, apply classify_complaint to each row, and write a validated results CSV.
    input: Input CSV file path containing complaint rows and an output CSV file path for results.
    output: A CSV file with header complaint_id, category, priority, reason, flag, and one line per input complaint.
    error_handling: Continue processing even if some rows fail, writing Other/Standard results with NEEDS_REVIEW for failed or malformed rows.
