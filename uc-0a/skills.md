# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: >
      Classifies a single citizen complaint into category, priority, reason, and flag
      using keyword-matching rules defined in agents.md.
    input: >
      A dict with keys:
        - complaint_id (str) — unique identifier for the complaint
        - description  (str) — free-form citizen complaint text
    output: >
      A dict with keys:
        - complaint_id (str)
        - category     (str) — exactly one of the 10 allowed category values
        - priority     (str) — one of: Urgent, Standard, Low
        - reason       (str) — one sentence citing specific words from the description
        - flag         (str) — "NEEDS_REVIEW" if category is ambiguous, blank otherwise
    error_handling: >
      If description is missing or empty, returns category=Other, priority=Low,
      flag=NEEDS_REVIEW, and reason="No description provided." — never raises.

  - name: batch_classify
    description: >
      Reads an input CSV of complaints, applies classify_complaint to each row,
      and writes a structured results CSV to the given output path.
    input: >
      - input_path  (str) — path to a CSV file containing at minimum the columns
                            complaint_id and description
      - output_path (str) — path where the results CSV will be written
    output: >
      A CSV file at output_path with columns: complaint_id, category, priority,
      reason, flag — one output row per input complaint row.
    error_handling: >
      If a row is missing required columns or classify_complaint raises an exception,
      that row is written with category=Other, priority=Low, flag=NEEDS_REVIEW, and
      a reason describing the failure. Processing continues for all remaining rows.
      A summary of failure count is printed to stdout. The output file is always
      written, even if some rows failed.
