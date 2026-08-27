# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: >
      Classifies a single citizen complaint into category, priority, reason,
      and optional flag.
    input: >
      A dictionary with at minimum a 'description' field containing the
      complaint text as a string.
    output: >
      A dictionary with keys: category (string from allowed list), priority
      (Urgent|Standard|Low), reason (one sentence citing specific words from
      description), flag (NEEDS_REVIEW or empty string).
    error_handling: >
      If description is empty or missing, return category: Other, priority:
      Low, reason: "No description provided", flag: NEEDS_REVIEW.

  - name: batch_classify
    description: >
      Reads an input CSV of complaints, applies classify_complaint to every
      row, and writes the output CSV with category, priority, reason, and
      flag columns added.
    input: >
      Path to input CSV (columns: id, description) and path for output CSV.
    output: >
      Output CSV written to the specified path with original columns plus
      category, priority, reason, flag.
    error_handling: >
      If input file does not exist or CSV is malformed, raise a clear error
      message and do not produce partial output. If a single row fails,
      classify it as Other/NEEDS_REVIEW and continue.
