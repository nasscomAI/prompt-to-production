skills:
  - name: classify_complaint
    description: Classifies a single complaint record into an allowed municipal category, priority level, justification reason, and review flag.
    input: Dict containing complaint fields including complaint_id, description, location, ward, city, and reported_by.
    output: Dict containing complaint_id, category, priority, reason, and flag.
    error_handling: If description is missing, empty, or genuinely ambiguous, set category to Other and flag to NEEDS_REVIEW. If non-fatal anomalies occur, maintain valid schema values.

  - name: batch_classify
    description: Reads an input CSV of citizen complaints, iteratively applies classify_complaint to each row, and writes structured results to a destination CSV.
    input: String path to input CSV file and string path to destination output CSV file.
    output: Writes destination CSV file with headers complaint_id,category,priority,reason,flag and returns integer count of processed rows.
    error_handling: Flags corrupted or unclassifiable rows without crashing; catches empty/missing fields gracefully and ensures complete batch completion.
