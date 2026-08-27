# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Triages a single citizen complaint row into structured classification fields.
    input: dict containing complaint row fields (complaint_id, description, location, etc.)
    output: dict with keys complaint_id, category, priority, reason, flag
    error_handling: Sets category to Other and flag to NEEDS_REVIEW if input is ambiguous or incomplete.

  - name: batch_classify
    description: Reads input test CSV file, applies classify_complaint to each row, and writes output CSV.
    input: input_path (str), output_path (str)
    output: Writes CSV with columns complaint_id, category, priority, reason, flag
    error_handling: Handles missing values gracefully, flags problematic rows, produces output CSV without crashing.
