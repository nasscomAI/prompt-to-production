# skills.md

skills:
  - name: classify_complaint
    description: Classify a single citizen complaint into category, priority, reason, and flag using the description field only.
    input: >
      A Python dictionary representing one CSV row with keys: complaint_id,
      date_raised, city, ward, location, description, reported_by, days_open.
      The description field contains the free-text citizen complaint.
    output: >
      A dictionary with keys: complaint_id (str), category (str — exact match from
      allowed list), priority (str — Urgent/Standard/Low), reason (str — one sentence
      citing specific words from description), flag (str — NEEDS_REVIEW or blank).
    error_handling: >
      If description is null or empty, return category: Other, priority: Low,
      reason: "No description provided", flag: NEEDS_REVIEW. Never raise exceptions
      on malformed input — always return a valid result dict.

  - name: batch_classify
    description: Read an input CSV of complaint rows, apply classify_complaint to each, and write results to an output CSV.
    input: >
      Two file paths as strings: input_path (path to a CSV file with columns:
      complaint_id, date_raised, city, ward, location, description, reported_by,
      days_open) and output_path (path to write the results CSV).
    output: >
      Writes a CSV file to output_path with columns: complaint_id, category, priority,
      reason, flag. Returns nothing but prints completion message.
    error_handling: >
      Skip rows that cause parse errors — log them to stderr and continue processing
      remaining rows. Always produce an output file even if some rows fail. Never crash
      on missing columns — treat missing description as empty string.
