# skills.md — UC-0A Complaint Classifier Skills

skills:
  - name: classify_complaint
    description: Accepts a single dictionary representing a complaint row and returns a dictionary containing complaint_id, category, priority, reason, and flag adhering strictly to RICE enforcement rules.
    input: Dictionary with keys complaint_id, date_raised, city, ward, location, description, reported_by, days_open.
    output: Dictionary with keys complaint_id, category, priority, reason, flag.
    error_handling: Handles missing or null fields by defaulting missing text to empty string, assigning default category 'Other', priority 'Standard', reason citing missing data, and flag 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV file containing raw citizen complaints, processes each row using classify_complaint skill, and writes structured results to the specified output CSV file.
    input: String file paths input_path (CSV input) and output_path (CSV output destination).
    output: Writes output CSV file containing headers complaint_id, category, priority, reason, flag.
    error_handling: Gracefully handles malformed CSV rows or missing files without crashing, ensuring valid output CSV is generated even if individual rows fail.
