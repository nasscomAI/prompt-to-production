# skills.md

skills:
  - name: classify_complaint
    description: Classify a single complaint row into category, priority, reason, and flag.
    input: A dictionary representing one input row, including complaint text and any metadata.
    output: A dictionary with keys: complaint_id, category, priority, reason, flag.
    error_handling: If the row is invalid or the description is missing, return category: Other, priority: Standard, reason: "Unable to classify due to missing description.", flag: NEEDS_REVIEW.

  - name: batch_classify
    description: Read an input CSV, apply classify_complaint to each row, and write the output CSV.
    input: Input file path to a CSV file with complaint rows.
    output: A CSV file containing classified rows with columns complaint_id, category, priority, reason, flag.
    error_handling: Continue processing remaining rows if some rows fail; include a fallback classification and NEEDS_REVIEW flag for unclassifiable rows.
