skills:
  - name: classify_complaint
    description: Classifies a single complaint description into category, priority, reason, and flag.
    input: A dictionary representing one CSV row containing complaint_id and description text.
    output: A dictionary containing complaint_id, category, priority, reason, and flag.
    error_handling: If description is empty or ambiguous, set category to Other and flag to NEEDS_REVIEW while still returning a valid output structure.

  - name: batch_classify
    description: Reads an input CSV file of complaints, applies classify_complaint to each row, and writes the results to an output CSV file.
    input: File path to input CSV containing complaint rows.
    output: Output CSV file with classification results for all rows.
    error_handling: If a row is malformed or missing fields, it should not crash the program; instead classify it as Other with NEEDS_REVIEW and continue processing remaining rows.