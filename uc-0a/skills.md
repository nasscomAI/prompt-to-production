# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: >
      Classifies a single complaint row into category, priority, reason,
      and NEEDS_REVIEW flag per the UC-0A enforcement rules.
    input: >
      dict — one row from the complaints CSV (complaint_id, description,
      location, ward, etc.).
    output: >
      dict — complaint_id, category (one of 10 allowed values), priority
      (Urgent/Standard/Low), reason (one sentence citing description words),
      flag (NEEDS_REVIEW or empty).
    error_handling: >
      Empty or missing description returns category Other, priority
      Standard, flag NEEDS_REVIEW. Never raises on malformed input.

  - name: batch_classify
    description: >
      Reads an input CSV, applies classify_complaint per row, and writes a
      results CSV with the classification schema.
    input: >
      input_path (CSV with complaint rows), output_path (CSV to write).
    output: >
      results CSV with columns complaint_id, category, priority, reason,
      flag; console summary of counts.
    error_handling: >
      Missing input file reports an error and exits without producing a
      partial file. A failing row is written as Other + NEEDS_REVIEW so the
      batch always completes; the batch never crashes.