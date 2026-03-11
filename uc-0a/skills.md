skills:
  - name: classify_complaint
    description: Takes one complaint row and returns category, priority, reason, and flag based on description text only.
    input: dict with keys complaint_id (str), description (str) — other fields present but ignored for classification
    output: dict with keys complaint_id (str), category (str from enum), priority (str: Urgent/Standard/Low), reason (str citing description words), flag (str: NEEDS_REVIEW or empty)
    error_handling: if description is null or empty, set category=Other, priority=Standard, reason="No description provided", flag=NEEDS_REVIEW

  - name: batch_classify
    description: Reads input CSV row by row, applies classify_complaint to each, writes results CSV with all output fields.
    input: input_path (str path to CSV), output_path (str path for results CSV)
    output: writes CSV file with columns complaint_id, category, priority, reason, flag — prints null count report before processing
    error_handling: if a row causes an error, write category=Other, flag=NEEDS_REVIEW for that row and continue — never crash the whole batch