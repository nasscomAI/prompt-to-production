skills:
  - name: classify_complaint
    description: Takes a single complaint dictionary and returns category, priority, reason, and flag fields.
    input: Dictionary containing complaint fields (complaint_id, description, location, etc.)
    output: Dictionary with complaint_id, category, priority, reason, flag
    error_handling: Assigns category 'Other', priority 'Low', and flag 'NEEDS_REVIEW' if description is empty or invalid.

  - name: batch_classify
    description: Reads input CSV of complaints, applies classify_complaint to each row, and writes classified output to CSV.
    input: input_path (str), output_path (str)
    output: CSV file with columns complaint_id, category, priority, reason, flag
    error_handling: Handles missing fields gracefully without interrupting batch execution.
