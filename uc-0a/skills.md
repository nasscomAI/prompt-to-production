# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single complaint into category and priority based on keywords in the complaint text.
    input: A dictionary row from the CSV containing complaint_id and complaint_text.
    output: A dictionary containing complaint_id, category, priority, reason, and flag.
    error_handling: If complaint_text is missing or empty, return category "other", priority "low", and flag "NEEDS_REVIEW".

  - name: batch_classify
    description: Reads the complaint CSV file, applies classification to each row, and writes results to an output CSV file.
    input: Input CSV file path containing complaint records.
    output: Output CSV file containing classified complaints with fields complaint_id, category, priority, reason, and flag.
    error_handling: If a row cannot be processed, record the row with category "error" and flag "row_error" instead of stopping execution.
