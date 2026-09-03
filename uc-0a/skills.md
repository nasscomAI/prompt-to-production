# skills.md — UC-0A Complaint Classifier Skills

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into exact category, priority, reason justification, and review flag.
    input: Dictionary containing complaint row data (must include 'complaint_id' and 'description').
    output: Dictionary with keys 'complaint_id', 'category', 'priority', 'reason', and 'flag'.
    error_handling: Sets flag to 'NEEDS_REVIEW' if description is ambiguous. For missing, null, or corrupted row inputs, falls back to category 'Other', priority 'Low', flag 'NEEDS_REVIEW', and reason 'Invalid or missing complaint description' without raising exceptions.

  - name: batch_classify
    description: Reads an input CSV file of citizen complaints, applies classify_complaint to each row, and writes the structured classification output to a CSV file.
    input: Input CSV file path (--input) and output CSV file path (--output).
    output: Writes results CSV file with header 'complaint_id,category,priority,reason,flag' and returns total count of processed rows.
    error_handling: Handles missing input CSV files, empty files, and malformed CSV rows gracefully, logging row-level errors while ensuring all valid rows are processed.
