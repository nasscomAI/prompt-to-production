skills:
  - name: complaint_categorizer
    description: Maps grievance text keywords to predefined municipal operational categories.
    input: Raw text string (complaint description).
    output: String category (Sanitation, Roads & Traffic, Water Supply, Electricity, Public Safety, or Unclassified).
    error_handling: Falls back to 'Unclassified' if text is empty, or 'Public Safety' as general default if no specific domain keywords match.

  - name: severity_priority_evaluator
    description: Enforces deterministic escalation rules for civic safety and infrastructure emergencies.
    input: Normalized lowercase text string (complaint description).
    output: Tuple of priority string (CRITICAL, HIGH, MEDIUM, LOW) and reason string.
    error_handling: Assigns LOW priority with an explicit EMPTY_TEXT flag if the input description is empty or null.

  - name: batch_csv_processor
    description: Reads city complaint CSV files, applies triage classification per row, and outputs structured results.
    input: File paths for input CSV and destination output CSV.
    output: CSV file containing complaint_id, category, priority, reason, and flag columns.
    error_handling: Catches row-level parsing exceptions, logs PARSE_ERROR flags, and continues processing subsequent records without crashing.