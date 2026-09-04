skills:
  - name: classify_complaint
    description: Deterministically classifies a single citizen complaint into allowed categories and priority levels with justification citations and review flags.
    input: A dictionary representing a complaint row with fields including complaint_id and description.
    output: A dictionary containing complaint_id, category, priority, reason, and flag according to schema constraints.
    error_handling: Returns category 'Other', priority 'Standard', an informative reason, and flag 'NEEDS_REVIEW' on missing, null, or malformed inputs without raising unhandled exceptions.

  - name: batch_classify
    description: Reads an input CSV of civic complaints, invokes classify_complaint on each row, and writes the classified records to an output CSV.
    input: input_path (str) to the source complaints CSV file, output_path (str) to the target destination CSV file.
    output: Generates a CSV file at output_path containing columns complaint_id, category, priority, reason, flag.
    error_handling: Gracefully handles missing files, invalid rows, and encoding variations, logging errors while completing remaining rows.
