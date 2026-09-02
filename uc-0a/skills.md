# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint row and determines its municipal category, priority rating, justification reason citing exact text, and review flag.
    input: dict representing a complaint record containing 'complaint_id', 'description', and optional metadata fields ('city', 'ward', 'location', 'reported_by', 'days_open').
    output: dict containing all original fields plus 'category' (str), 'priority' (str), 'reason' (str), and 'flag' (str).
    error_handling: When description is missing, empty, or unclassifiable, assigns category 'Other', priority 'Standard', flag 'NEEDS_REVIEW', and sets reason detailing the data quality issue.

  - name: batch_classify
    description: Streams an input CSV file of citizen complaints, processes each row via classify_complaint, handles malformed records with warnings, and writes an enriched output CSV.
    input: input_path (str) to source CSV, output_path (str) destination file path.
    output: writes CSV file with original columns plus category, priority, reason, flag; returns summary statistics of processed rows.
    error_handling: Handles missing files, unreadable rows, and empty columns gracefully by logging warnings and preserving row-by-row structure without terminating the batch.