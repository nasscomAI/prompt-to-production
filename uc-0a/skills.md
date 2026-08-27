# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies an individual civic complaint record into a standardized category, priority level, citation-backed reason, and review flag based on strict taxonomy rules and severity keywords.
    input: dict containing complaint record fields (complaint_id, description, location, ward, city, reported_by, days_open).
    output: dict with keys (complaint_id, category, priority, reason, flag).
    error_handling: On missing or corrupted fields, returns category="Other", priority="Standard" (or "Urgent" if severity triggers present), reason explaining the issue with cited details, and flag="NEEDS_REVIEW".

  - name: batch_classify
    description: Reads an input CSV file of citizen complaints, processes each row through classify_complaint with fault tolerance, and writes the resulting structured classifications to a destination CSV file.
    input: input_path (str: path to input CSV file), output_path (str: path to output CSV file).
    output: None (writes a CSV file with columns complaint_id, category, priority, reason, flag).
    error_handling: Handles malformed rows and missing columns gracefully without crashing, logs errors per row, and guarantees complete and valid output CSV generation.
