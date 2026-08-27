# skills.md

skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint to determine its category, priority (triggered by severity keywords), and a cited reason.
    input: complaint_text (string)
    output: A structured object with fields: category (taxonomy match), priority (Urgent/Standard/Low), reason (cited sentence), and flag (NEEDS_REVIEW or blank).
    error_handling: If text is empty or category is undecidable, defaults to category "Other" and sets flag to "NEEDS_REVIEW".

  - name: batch_classify
    description: Iterates through a CSV of citizen complaints, applying classify_complaint to each row and appending results to an output file.
    input: input_file_path (string), output_file_path (string)
    output: A result CSV containing all input columns plus category, priority, reason, and flag columns.
    error_handling: Gracefully skips rows that are not in CSV format or are missing a description field; logs FileNotFoundError if input path is invalid.
