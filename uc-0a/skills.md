skills:
  - name: classify_complaint
    description: Classify a single citizen complaint row and return category, priority, reason, and flag.
    input: A dictionary with fields {complaint_id, date_raised, city, ward, location, description, reported_by, days_open}
    output: A dictionary with fields {complaint_id, category, priority, reason, flag} where category is exact string from allowed taxonomy, priority is Urgent or Standard, reason is one sentence citing description text, and flag is NEEDS_REVIEW or blank
    error_handling: If description is empty or incomprehensible, output category=Other, priority=Standard, reason="Unable to parse complaint description", flag=NEEDS_REVIEW. If multiple valid categories exist, set flag=NEEDS_REVIEW and choose most likely category. Normalize severity keywords to lowercase before matching.

  - name: batch_classify
    description: Read CSV with complaint rows, apply classify_complaint to each, and write results to output CSV.
    input: Path to input CSV file with columns {complaint_id, date_raised, city, ward, location, description, reported_by, days_open}
    output: Path to output CSV file with columns {complaint_id, category, priority, reason, flag} where each row has been classified according to agents.md rules
    error_handling: If input file missing, raise FileNotFoundError. If row parsing fails, skip row and log warning. If output path is not writable, raise IOError. Validate all output categories against allowed taxonomy before writing.
