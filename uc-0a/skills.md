# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into category, priority, reason, and flag
    input: dict with keys complaint_id, location, description
    output: dict with keys complaint_id, category, priority, reason, flag
    error_handling: Returns category "Other" with flag "NEEDS_REVIEW" when description is empty or ambiguous

  - name: batch_classify
    description: Reads input CSV, classifies each row, writes results CSV
    input: input_path (str), output_path (str) - both file paths
    output: int - number of rows processed
    error_handling: Gracefully handles bad rows, continues processing, reports errors at end
