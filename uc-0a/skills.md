skills:
  - name: classify_complaint
    description: Classify a single civic complaint row into a standardized category, priority level, justification reason citing specific words from the description, and an ambiguity flag.
    input: dict representing a complaint row with fields such as complaint_id, description, location, etc.
    output: dict with keys complaint_id, category, priority, reason, flag
    error_handling: Handles missing fields or empty descriptions by assigning category 'Other', priority 'Standard', reason 'Missing or empty description in input', and flag 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV file of civic complaints, processes each row using classify_complaint, and writes the structured classification results to a target CSV file.
    input: input_path (str path to input CSV), output_path (str path to output CSV)
    output: None (writes results to output CSV containing complaint_id, category, priority, reason, flag)
    error_handling: Catches malformed or unreadable rows without terminating execution, flags missing data with NEEDS_REVIEW, and ensures the output file is produced completely.
