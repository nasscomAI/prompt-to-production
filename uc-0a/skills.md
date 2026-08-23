# skills.md — UC-0A Complaint Classifier Skills

skills:
  - name: classify_complaint
    description: Takes a single complaint dictionary row and returns structured classification results (category, priority, reason, flag) strictly adhering to RICE enforcement rules.
    input: Dictionary representing a CSV row with keys 'complaint_id', 'description', etc.
    output: Dictionary with keys 'complaint_id', 'category', 'priority', 'reason', 'flag'.
    error_handling: If input row is malformed or description is empty, set category to 'Other', priority to 'Standard', reason to 'Missing description text', and flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV file of citizen complaints, processes each row via classify_complaint skill, validates outputs, and writes the results CSV file.
    input: input_path (str path to input CSV), output_path (str path to output CSV).
    output: Writes CSV file with header [complaint_id, category, priority, reason, flag] and prints completion status.
    error_handling: Handles missing input files gracefully, skips invalid headers, and flags unparseable rows as NEEDS_REVIEW without crashing.
