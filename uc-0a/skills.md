skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint record into an exact category and priority with evidence-based reasoning and ambiguity flagging.
    input: dict representing a single complaint row with keys (complaint_id, date_raised, city, ward, location, description, reported_by, days_open)
    output: dict containing keys: complaint_id, category, priority, reason, flag
    error_handling: If description is missing, empty, or ambiguous, assigns category 'Other', flag 'NEEDS_REVIEW', and notes the issue in reason.

  - name: batch_classify
    description: Reads a CSV of civic complaints, processes each row with classify_complaint, and writes the structured classification results to a target CSV file.
    input: input_path (str - path to input CSV file), output_path (str - path to output CSV file)
    output: None (writes results CSV to output_path with columns: complaint_id, category, priority, reason, flag)
    error_handling: Handles missing files, malformed rows, or null fields safely without crashing; ensures all processed rows are written to output with appropriate review flags.

