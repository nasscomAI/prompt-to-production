# skills.md

skills:
  - name: classify_complaint
    description: Classify a single complaint row into category, priority, reason, and flag using keyword matching.
    input: dict with keys complaint_id, description (and other CSV columns which are ignored)
    output: dict with keys: complaint_id, category, priority, reason, flag
    error_handling: If description is missing or null, returns category=Other, priority=Low, flag=NEEDS_REVIEW with reason citing the missing input.

  - name: batch_classify
    description: Read an input CSV of complaints, classify each row, and write results to an output CSV.
    input: input_path (str) pointing to a CSV file, output_path (str) for the results CSV
    output: Writes a CSV with columns complaint_id, category, priority, reason, flag
    error_handling: Skips malformed rows gracefully, logs warnings to stderr, produces output CSV even if some rows fail classification.
