# skills.md

skills:
  - name: classify_complaint
    description: Analyzes a single complaint description to map it to the defined taxonomy and determine priority.
    input: dict {description, complaint_id, ...}
    output: dict {complaint_id, category, priority, reason, flag}
    error_handling: "If ambiguous or mapping fails, return category: Other and flag: NEEDS_REVIEW."

  - name: batch_classify
    description: Reads a CSV of complaints, applies classify_complaint to each row, and saves the results to a CSV.
    input: string (input_path), string (output_path)
    output: writes results to CSV
    error_handling: "Skips invalid rows, handles missing descriptions as category: Other with flag: NEEDS_REVIEW."
