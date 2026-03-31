# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row to determine category, priority, reason, and flag.
    input: A dictionary representing one complaint row (containing the complaint description).
    output: A dictionary containing keys: complaint_id, category, priority, reason, and flag.
    error_handling: If the description is entirely ambiguous or empty, return category as "Other" and flag as "NEEDS_REVIEW".

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint per row, and writes an output CSV.
    input: Two strings representing the input CSV path and the output CSV path.
    output: A CSV file written to the output path containing standard fields plus classified columns.
    error_handling: Must flag nulls gracefully, not crash on malformed rows, and ensure output is produced even if some rows fail.
