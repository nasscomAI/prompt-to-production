# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Takes one complaint dictionary row and returns classified category, priority, reason, and flag.
    input: Dictionary with keys complaint_id, date_raised, city, ward, location, description, reported_by, days_open.
    output: Dictionary with keys complaint_id, category, priority, reason, flag.
    error_handling: Flags blank/null description rows as NEEDS_REVIEW and sets category to Other.

  - name: batch_classify
    description: Reads input CSV file, applies classify_complaint to each row, and writes output CSV file.
    input: File paths input_path and output_path.
    output: Writes results CSV file containing classified columns.
    error_handling: Handles missing input files gracefully and ensures non-crashing execution on corrupt rows.
