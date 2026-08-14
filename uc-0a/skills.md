# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Takes a single raw civic complaint row dictionary and maps it to a validated taxonomy category, priority tier, citation reason, and review flag.
    input: dict containing complaint_id, date_raised, city, ward, location, description, reported_by, days_open
    output: dict with keys [complaint_id, category, priority, reason, flag]
    error_handling: Handles missing descriptions, unparseable fields, and ambiguous rows by falling back to category 'Other' or flagging with 'NEEDS_REVIEW' without throwing exceptions.

  - name: batch_classify
    description: Ingests an input CSV file of civic complaints, processes each row sequentially through classify_complaint, and writes out a validated results CSV file.
    input: input_path (str) - path to source CSV file; output_path (str) - target destination path
    output: Writes results CSV file to output_path
    error_handling: Gracefully handles malformed input rows and continues processing remaining rows.
