# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into category, priority, reason, and flag
    input: "dict with keys: complaint_id, date_raised, city, ward, location, description, reported_by, days_open"
    output: "dict with keys: complaint_id, category, priority, reason, flag"
    error_handling: "If description is insufficient to determine category, return category 'Other' and flag 'NEEDS_REVIEW'"

  - name: batch_classify
    description: Reads input CSV, applies classify_complaint to each row, writes results to output CSV
    input: "input_path (str): path to input CSV file, output_path (str): path to output CSV file"
    output: "None (writes CSV file to output_path)"
    error_handling: "Skip rows that fail to parse, log errors, continue processing remaining rows, produce output even if some rows fail"
