# skills.md

skills:
  - name: classify_complaint
    description: Classify a single complaint into category, priority, and reason with optional NEEDS_REVIEW flag.
    input: "Complaint object (dict): complaint_id, date_raised, city, ward, location, description, reported_by, days_open"
    output: "Classification object (dict): complaint_id, category, priority, reason, flag"
    error_handling: "If description is empty, return category: Other, priority: Standard, reason: 'No description provided', flag: NEEDS_REVIEW. If severity keywords present but priority not Urgent, reject and re-run. If reason does not cite description, reject and re-run."

  - name: batch_classify
    description: Read CSV file, classify all complaints using classify_complaint, write results to output CSV.
    input: "CSV file path (string), Output CSV path (string). CSV columns: complaint_id, date_raised, city, ward, location, description, reported_by, days_open"
    output: "CSV file with columns: complaint_id, category, priority, reason, flag. Also prints summary: rows processed, Urgent count, Standard count, Low count, NEEDS_REVIEW count"
    error_handling: "If row fails classification, log error and default to category: Other, priority: Standard, reason: 'Classification failed', flag: NEEDS_REVIEW. Continue processing remaining rows."
