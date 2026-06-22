# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: >
      Classifies a single citizen complaint row by assigning a category, priority,
      and reason based solely on the complaint description text, and sets a flag
      if the category is ambiguous.
    input: >
      dict — a single row from the complaints CSV with at minimum a 'complaint_id' key
      and a 'description' key containing the complaint text.
    output: >
      dict — with keys: complaint_id (str), category (str — one of the 10 allowed),
      priority (str — "Urgent" or "Standard"), reason (str — one sentence citing
      specific description words), flag (str — "NEEDS_REVIEW" or empty string "").
    error_handling: >
      If description is empty or None, set category = "Other", priority = "Standard",
      reason = "Empty description — cannot determine category", flag = "NEEDS_REVIEW".
      If description contains text but no keywords match any category, use category = "Other".

  - name: batch_classify
    description: >
      Reads the input CSV file containing citizen complaints, applies classify_complaint
      to every row, and writes the classified results to an output CSV file.
    input: >
      input_path (str) — path to the input CSV file with at minimum complaint_id and
      description columns. output_path (str) — path where the results CSV will be written.
    output: >
      None — writes the output CSV file to output_path with columns: complaint_id,
      category, priority, reason, flag. Prints summary stats to stdout (total rows,
      rows classified, rows flagged).
    error_handling: >
      If input file does not exist or cannot be read, raises FileNotFoundError with
      a descriptive message. If a specific row fails classification (e.g. malformed),
      that row is written with category = "Other", priority = "Standard",
      reason = "Error processing row", flag = "NEEDS_REVIEW" and processing continues.
      The function never crashes on bad data — it processes all rows and reports
      errors per-row.