skills:
  - name: classify_complaint
    description: Classifies a single complaint record into category, priority, reason, and review flag.
    input: dict representing a single complaint row (keys: complaint_id, description, etc.)
    output: dict containing complaint_id, category, priority, reason, flag
    error_handling: If fields are missing or empty, default category to Other, set flag to NEEDS_REVIEW, and state the missing information in the reason.

  - name: batch_classify
    description: Reads the input CSV, applies classify_complaint to each row, and writes the results to an output CSV.
    input: input_path (str) to the source CSV file and output_path (str) to the target CSV file.
    output: Writes output CSV file containing the classified complaints.
    error_handling: Handles missing input file gracefully, skips malformed rows, and ensures the script does not crash on corrupt data.