# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Receives a single complaint record dictionary and outputs category, priority, justification reason, and review flag according to RICE enforcement rules.
    input: dict containing complaint_id, description, days_open, location, ward, city
    output: dict containing complaint_id, category, priority, reason, flag
    error_handling: If description is missing or empty, sets category to Other, priority to Low, reason to 'Missing complaint description', and flag to NEEDS_REVIEW.

  - name: batch_classify
    description: Processes an input CSV file containing citizen complaints, applies classify_complaint to each row, and writes the classified records to the target output CSV file.
    input: input_path (str), output_path (str)
    output: Writes output CSV file containing complaint_id, category, priority, reason, flag, city, ward, location, description
    error_handling: Handles missing fields or malformed CSV rows gracefully without crashing, logging errors and assigning NEEDS_REVIEW flags to unparseable rows.

