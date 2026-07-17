# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: >
      Classifies a single complaint row into category, priority, reason,
      and flag using only the description field and the fixed schema in
      agents.md.
    input: >
      Dict with at minimum:
        - complaint_id  (string)
        - description   (string)
      All other CSV fields are passed through unchanged.
    output: >
      Dict with all input fields plus:
        - category  (string) — exactly one of the 10 allowed values
        - priority  (string) — Urgent | Standard | Low
        - reason    (string) — one sentence citing words from description
        - flag      (string) — "NEEDS_REVIEW" or ""
      Rules applied:
        1. Category matched via keyword lookup against description (case-insensitive).
        2. Priority set to Urgent if any severity keyword is found in description;
           Standard if category is determined with confidence; Low otherwise.
        3. If two or more categories match equally, category → Other, flag → NEEDS_REVIEW.
        4. If description is blank or < 3 words, all fields set to safe defaults
           and flag → NEEDS_REVIEW.
    error_handling: >
      If the row dict is missing the description key entirely, return the row
      with category: "Other", priority: "Low", reason: "Missing description
      field", flag: "NEEDS_REVIEW". Do not raise an exception — the batch must
      continue processing remaining rows.

  - name: batch_classify
    description: >
      Reads an input CSV, applies classify_complaint to every row, and writes
      a results CSV with the four added fields.
    input: >
      - input_path   (string) — path to source CSV with complaint rows
      - output_path  (string) — path to write results CSV
    output: >
      Results CSV at output_path containing all original columns plus:
        category, priority, reason, flag
      One row per input row; no rows dropped.
      Prints a summary line: "Classified N rows. NEEDS_REVIEW: M."
    error_handling: >
      - If input_path does not exist: print error message and exit — do not
        create an empty output file.
      - If a single row fails classification (e.g. corrupt encoding): write the
        row with category: "Other", priority: "Low", reason: "Row parse error",
        flag: "NEEDS_REVIEW" and continue. Never crash the entire batch on a
        single bad row.
      - If output_path directory does not exist: print error and exit cleanly.
