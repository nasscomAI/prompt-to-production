# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single complaint record into category, priority, reason, and optional review flag.
    input: Dictionary representing a complaint row containing complaint_id, description, and optional metadata fields (date_raised, city, ward, location, reported_by, days_open).
    output: Dictionary with keys complaint_id, category, priority, reason, flag.
    error_handling: If description is missing or null, set category to 'Other', priority to 'Low', reason to 'Missing description field in input', and flag to 'NEEDS_REVIEW'. If classification is ambiguous, set category to 'Other' and flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV of citizen complaints, applies classify_complaint row by row, and writes the structured classification results to an output CSV.
    input: File paths input_path (string path to input CSV) and output_path (string path to output CSV).
    output: CSV file at output_path containing headers complaint_id, category, priority, reason, flag.
    error_handling: Flags missing or corrupted rows, does not crash on bad rows, and produces complete output CSV even if individual rows fail.
