skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into category, priority, and reason, flagging ambiguity.
    input: Dictionary representing a single CSV row with at least 'complaint_id' and 'description' keys.
    output: Dictionary with keys 'complaint_id', 'category', 'priority', 'reason', 'flag'.
    error_handling: If description is missing or invalid, classifies as 'Other', sets priority to 'Standard', sets flag to 'NEEDS_REVIEW', and notes the failure in the 'reason'.

  - name: batch_classify
    description: Reads the input CSV file, applies classify_complaint to each row, and writes the output CSV file.
    input: Strings path to input CSV and path to output CSV.
    output: Writes output CSV.
    error_handling: Handles file not found errors, handles processing errors on a per-row basis by writing a flagged row, and ensures the script does not crash.
