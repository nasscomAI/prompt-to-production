# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into a category and priority with a cited reason.
    input: A dictionary representing a single row from the complaint CSV (e.g., {'complaint_id': '...', 'description': '...'}).
    output: A dictionary with keys: complaint_id, category, priority, reason, flag.
    error_handling: If 'description' is missing or empty, set category to "Other", priority to "Low", and flag to "NEEDS_REVIEW".

  - name: batch_classify
    description: Reads an input CSV of complaints, classifies each row, and writes the results to an output CSV.
    input: 'input_path' (string) and 'output_path' (string).
    output: None (writes to file).
    error_handling: Skips malformed rows and ensures the output CSV is created even if some rows fail.
