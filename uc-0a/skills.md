# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classify a single citizen complaint row into category, priority, reason, and flag.
    input: >
      A dictionary (dict) with keys: complaint_id (str), description (str).
      The description is free-text from a citizen complaint.
    output: >
      A dictionary (dict) with keys: complaint_id (str), category (str — one of the 10 allowed values),
      priority (str — Urgent/Standard/Low), reason (str — one sentence citing words from description),
      flag (str — "NEEDS_REVIEW" or empty string).
    error_handling: >
      If description is empty or null, return category: Other, priority: Low,
      reason: "No description provided", flag: NEEDS_REVIEW.
      If description is ambiguous across multiple categories, pick the best fit,
      set flag to NEEDS_REVIEW, and explain ambiguity in reason.

  - name: batch_classify
    description: Read an input CSV of complaints, classify each row using classify_complaint, and write results to an output CSV.
    input: >
      Two file paths (str): input_path (path to a CSV with columns including complaint_id and description)
      and output_path (path where results CSV will be written).
    output: >
      A CSV file written to output_path with columns: complaint_id, category, priority, reason, flag.
      One row per input complaint. Returns nothing (writes to disk).
    error_handling: >
      If a row fails to parse or has missing fields, write a row with category: Other,
      priority: Low, reason: "Failed to parse row", flag: NEEDS_REVIEW.
      Never crash on bad rows — always produce output for every input row.
      If input file does not exist, raise FileNotFoundError with a clear message.
