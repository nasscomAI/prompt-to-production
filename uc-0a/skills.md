# skills.md — UC-0A: Complaint Classifier

skills:
  - name: classify_complaint
    description: >
      Classifies a single complaint row by category, priority, reason, and
      review flag based on the complaint description text.
    input: >
      A dictionary with keys: complaint_id (string), description (string),
      and any other CSV row fields (used for context only, not classification).
    output: >
      A dictionary with keys: complaint_id (string), category (string, exact
      match from allowed list), priority (string: Urgent/Standard/Low),
      reason (string, one sentence citing description words), flag (string:
      NEEDS_REVIEW or empty).
    error_handling: >
      If description is empty or missing, set category to Other, priority to
      Standard, reason to "Empty description — cannot classify", flag to
      NEEDS_REVIEW. Never crash on bad input.

  - name: batch_classify
    description: >
      Reads an input CSV of complaints, applies classify_complaint to each
      row, and writes results to an output CSV.
    input: >
      Input file path (string) to a CSV with complaint rows. Output file
      path (string) for the results CSV.
    output: >
      A CSV file with columns: complaint_id, category, priority, reason,
      flag. Written to the output path.
    error_handling: >
      If a row fails classification, include it in output with category=Other,
      flag=NEEDS_REVIEW, and reason describing the error. Never skip rows.
      Produce output even if some rows fail.
