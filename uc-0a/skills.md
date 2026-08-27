# skills.md

skills:
  - name: classify_complaint
    description: Classify a single complaint row to determine category, priority, reason, and flag.
    input: A single dictionary or JSON object representing one complaint row (e.g., complaint_id, description, location).
    output: A dictionary containing exact keys - category, priority, reason, and flag out.
    error_handling: Return category 'Other', flag 'NEEDS_REVIEW', and a reason explaining the issue if input is missing critical fields or is severely malformed.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint per row, and writes an output CSV.
    input: The file path of the input CSV (e.g., test_pune.csv) and the desired file path for the output CSV.
    output: Writes to the output CSV and returns the count of successful and failed classifications.
    error_handling: Must flag nulls or bad rows gracefully without crashing, and produce output even if some rows fail to parse.
