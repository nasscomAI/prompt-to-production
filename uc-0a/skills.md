skills:
  - name: classify_complaint
    description: Classifies a single civic complaint row into category, priority, justification reason, and review flag based on strict taxonomy and severity triggers.
    input: Dictionary representing a CSV complaint row with keys complaint_id, date_raised, city, ward, location, description, reported_by, days_open.
    output: Dictionary with keys complaint_id, category, priority, reason, flag conforming strictly to allowed values.
    error_handling: Handles missing fields or malformed strings gracefully by assigning category 'Other', priority 'Standard', citing missing information in reason, and setting flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV file of civic complaints, processes each row via classify_complaint, handles bad/null rows without crashing, and writes the structured classification to a results CSV.
    input: File paths input_path (str) and output_path (str).
    output: Writes output CSV with columns complaint_id, category, priority, reason, flag and returns summary count of processed rows.
    error_handling: Catches file I/O errors and individual row formatting anomalies, logging warnings and continuing batch execution to ensure complete output generation.
