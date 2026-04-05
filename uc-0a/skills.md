# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classify a single complaint row by assigning category, priority, reason, and ambiguity flag based on description text.
    input: Dict with keys complaint_id, description (and optional other metadata that is ignored for classification).
    output: Dict with keys complaint_id, category, priority, reason, flag where category is an exact allowed string, priority is Urgent/Standard/Low, reason is one sentence citing specific words, flag is NEEDS_REVIEW or blank.
    error_handling: If description is missing or empty, raise ValueError. If no reasonable category match exists, set category to Other and flag to NEEDS_REVIEW.

  - name: batch_classify
    description: Read input CSV, classify each row using classify_complaint, and write results CSV with all original columns plus category, priority, reason, flag.
    input: File path to CSV with columns complaint_id, description (and others), and output file path.
    output: CSV file with all input columns preserved plus four new columns: category, priority, reason, flag. Returns count of successfully classified rows, null counts, and any errors encountered.
    error_handling: Log row index and error message for any row that fails classification. Write successfully classified rows to output even if some rows fail. Do not crash on bad input — flag the row and continue.
