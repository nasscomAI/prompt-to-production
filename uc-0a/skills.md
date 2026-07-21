skills:
  - name: classify_complaint
    description: Takes one complaint row and returns its category, priority, reason, and review flag based on keyword and severity matching against the description text.
    input: A dict/row with at least a description-like field (description, complaint, complaint_text, complaint_desc, issue_description, or text) and an id-like field (complaint_id, id, ID, or ticket_id).
    output: A dict with keys complaint_id, category (one of the 10 allowed schema values), priority (Urgent, Standard, or Low), reason (a sentence citing the matched keyword(s)), and flag (NEEDS_REVIEW or blank).
    error_handling: If the description is missing or empty, returns category "Other", priority "Standard", flag "NEEDS_REVIEW", and a reason stating no description was provided — it never raises an exception for missing/invalid input.

  - name: batch_classify
    description: Reads an input CSV of complaint rows, applies classify_complaint to each row, and writes a results CSV with the classification columns.
    input: input_path (path to a CSV with a header row and complaint rows) and output_path (path to write the results CSV to).
    output: A CSV file at output_path with columns complaint_id, category, priority, reason, flag — one row per input row, always written even if some rows fail.
    error_handling: If the input file doesn't exist or has no header row, raises a clear error and does not silently produce an empty/wrong file. Any row that raises an exception during classification does not crash the batch — it is written to the output as category "Other", priority "Standard", flag "NEEDS_REVIEW", with a reason explaining the failure, and the run continues to the next row.