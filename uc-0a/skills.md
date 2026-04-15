skills:
  - name: classify_complaint
    description: Classify a single complaint into category, prioritcsv row with complaint_id, date_raised, city, ward, location, description, reported_by, days_open,string format
    output: Dictionary with complaint_id, category, priority, reason, flag, format is string
    error_handling: If the description is genuinely ambiguous or the category cannot be determined, returns category as "Other" and flag as "NEEDS_REVIEW".

  - name: batch_classify
    description: reads input CSV, applies classify_complaint per row, writes output CSV
    input: csv file with complaint_id, date_raised, city, ward, location, description, reported_by, days_open
    output: csv file with complaint_id, category, priority, reason, flag
    error_handling: If the input file is invalid or ambiguous, return an error message.
