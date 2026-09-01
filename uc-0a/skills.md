# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: >
      Classify a single complaint row into category, priority, reason, and flag
      using the fixed taxonomy and severity keyword rules.
    input: >
      dict with keys: complaint_id (str), description (str), location (str), date (str).
      Description is the only field used for classification.
    output: >
      dict with keys: complaint_id (str), category (str from allowed list),
      priority (str: Urgent/Standard/Low), reason (str: one sentence citing description words),
      flag (str: NEEDS_REVIEW or empty).
    error_handling: >
      If description is null or empty, set category to Other, flag to NEEDS_REVIEW,
      and reason to "No description provided."
      If complaint_id is missing, set it to "UNKNOWN".

  - name: batch_classify
    description: >
      Read input CSV, apply classify_complaint to each row, and write results CSV.
      Ensures every input row produces an output row.
    input: >
      Two file paths: input_path (str) to CSV with columns complaint_id, description,
      location, date; output_path (str) for results CSV.
    output: >
      Writes CSV file with columns: complaint_id, category, priority, reason, flag.
      Also returns count of classified and flagged rows.
    error_handling: >
      If a row is malformed or missing required fields, classify it with category: Other
      and flag: NEEDS_REVIEW rather than skipping. Never crash on bad rows.
      If input file is empty, write empty CSV with headers and return count 0.
