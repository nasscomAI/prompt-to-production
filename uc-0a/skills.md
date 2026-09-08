skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint record into category, priority, reason, and flag using strict municipal taxonomy and severity enforcement.
    input: Dictionary representing a single complaint row containing complaint_id, description, location, ward, city, days_open.
    output: Dictionary with keys complaint_id, category, priority, reason, flag.
    error_handling: If description is missing, empty, or unparseable, returns category 'Other', priority 'Low', reason 'Missing or empty complaint description', and flag 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV of citizen complaints, executes classify_complaint on each row, and writes the structured classification results to a target CSV file.
    input: input_path (string file path to CSV), output_path (string file path to write output CSV).
    output: Writes output CSV containing columns complaint_id, category, priority, reason, flag.
    error_handling: Flags malformed rows without crashing, skips unreadable entries with a warning, and guarantees complete file generation even on partial row failures.
