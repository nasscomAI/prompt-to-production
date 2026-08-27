skills:
  - name: classify_complaint
    description: Classifies a single complaint record into an allowed category, priority level, justification reason, and review flag based on description keywords and severity triggers.
    input: dict containing complaint fields (complaint_id, description, location, etc.)
    output: dict with keys (complaint_id, category, priority, reason, flag)
    error_handling: Returns category 'Other' and flag 'NEEDS_REVIEW' on missing/corrupt description; defaults priority to 'Standard' if unresolvable.

  - name: batch_classify
    description: Reads an input CSV of civic complaints, runs classify_complaint on each row safely handling malformed rows, and writes the structured results to an output CSV file.
    input: input_path (str path to input CSV), output_path (str path to output CSV)
    output: None (writes CSV file with classified results)
    error_handling: Catches row-level parsing errors, flags invalid rows with NEEDS_REVIEW, and ensures complete output generation without crashing.
