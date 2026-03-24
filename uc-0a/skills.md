# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single complaint description into category, priority, reason, and flag fields according to the UC-0A taxonomy and enforcement rules.
    input: A complaint description string (e.g., "Pothole on Oak Street near school, child fell yesterday").
    output: A JSON object with four fields — category (string), priority (Urgent/Standard/Low), reason (one-sentence string), flag (NEEDS_REVIEW or empty string).
    error_handling: If category cannot be determined from description alone, output category as Other and set flag to NEEDS_REVIEW. If required fields are missing from input, output an error message citing the missing field.

  - name: batch_classify
    description: Reads the input CSV file, applies classify_complaint skill to each complaint row, and writes results to an output CSV file with additional classification columns.
    input: CSV file path with a description column (or Description column); optionally other complaint metadata columns.
    output: CSV file containing original columns plus new columns — category, priority, reason, flag — one classified row per input complaint.
    error_handling: If input CSV is malformed or missing the description column, log an error and halt. If classify_complaint fails on a single row, log the row number and description, set category to Other, priority to Standard, reason to "Error processing complaint", and flag to NEEDS_REVIEW, then continue to next row.
