skills:
  - name: classify_complaint
    description: Classify a single civic complaint description into category, priority, reason, and flag.
    input: One complaint row containing description text.
    output: category, priority, reason, flag.
    error_handling: If category cannot be determined, set category to "Other" and flag as "NEEDS_REVIEW".

  - name: batch_classify
    description: Read the input CSV file, apply classify_complaint to each row, and write results to an output CSV file.
    input: Input CSV file path containing complaint records.
    output: Output CSV file containing complaint_id, category, priority, reason, and flag.
    error_handling: If the file cannot be read or written, return an error message and stop execution.