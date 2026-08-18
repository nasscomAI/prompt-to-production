# skills.md — UC-0A Skills Definition

skills:
  - name: classify_complaint
    description: Classifies a single complaint record into category, priority, reason, and flag using strict taxonomy and severity keyword matching.
    input: Dictionary representing one complaint row (containing complaint_id, description, etc.).
    output: Dictionary with keys complaint_id, category, priority, reason, flag.
    error_handling: Flags row as NEEDS_REVIEW and sets category to Other if description is empty, null, or ambiguous.

  - name: batch_classify
    description: Reads an input CSV file of municipal complaints, applies classify_complaint per row, and writes the output CSV file.
    input: String input_path (CSV file path) and String output_path (CSV destination path).
    output: Writes output CSV with columns complaint_id, category, priority, reason, flag.
    error_handling: Handles missing rows, null values, or formatting errors gracefully without crashing the pipeline.

