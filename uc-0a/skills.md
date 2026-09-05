# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into exact category, priority, reason, and flag.
    input: dictionary representing a single complaint row (keys: complaint_id, description, etc.)
    output: dictionary with keys complaint_id, category, priority, reason, flag
    error_handling: Default category to Other and flag as NEEDS_REVIEW if description is empty or ambiguous.

  - name: batch_classify
    description: Reads an input CSV file of complaints, classifies each row, and writes the output CSV file.
    input: input_path (string), output_path (string)
    output: boolean status or written output file path
    error_handling: Handles missing files or malformed CSV rows gracefully without stopping execution.
