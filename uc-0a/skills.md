skills:
  - name: classify_complaint
    description: Classify a single complaint row into the UC-0A schema.
    input: A dictionary representing one CSV row, including at least the complaint text or description field and optional complaint_id.
    output: A dictionary with keys: complaint_id, category, priority, reason, flag.
    error_handling: If the row is missing required fields or is ambiguous, return a valid output row using `Other` as the category when needed, set `flag` to `NEEDS_REVIEW`, and still provide a reason.

  - name: batch_classify
    description: Read an input CSV of complaints, apply classify_complaint to each row, and write a results CSV.
    input: Two file paths: an input CSV path and an output CSV path.
    output: A written CSV file with header row and one result row per input complaint.
    error_handling: Continue processing remaining rows even if some rows are invalid; write output rows for all input rows and mark problematic rows with `flag: NEEDS_REVIEW`.
