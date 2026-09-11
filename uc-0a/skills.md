# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag.
    input: One dictionary row with fields complaint_id and description (string, may be null).
    output: Dictionary with keys complaint_id, category, priority, reason, flag.
    error_handling: Returns category=Other, priority=Low, flag=NEEDS_REVIEW with reason stating the description was missing when input description is null or empty.

  - name: batch_classify
    description: Reads an input CSV, applies classify_complaint to every row, and writes a results CSV.
    input: input_path (string, path to test CSV), output_path (string, path to write results CSV).
    output: Writes a CSV with columns complaint_id, category, priority, reason, flag; prints a summary of counts per category.
    error_handling: Handles missing rows or malformed CSV without crashing; classifies each row independently, skips failed rows with a warning, and still writes output for rows that succeeded.