skills:
  - name: classify_complaint
    description: Takes one complaint dictionary row and returns structured classification (complaint_id, category, priority, reason, flag).
    input: dict containing complaint_id, description, etc.
    output: dict with keys complaint_id, category, priority, reason, flag
    error_handling: Falls back to category 'Other' and sets flag to 'NEEDS_REVIEW' if description is empty or invalid.

  - name: batch_classify
    description: Reads input CSV file, executes classify_complaint for each row, and writes structured results CSV.
    input: input CSV file path, output CSV file path
    output: Writes CSV with columns complaint_id, category, priority, reason, flag
    error_handling: Handles missing input file gracefully and logs row-level errors without crashing execution.
