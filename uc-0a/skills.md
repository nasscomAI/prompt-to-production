# skills.md

skills:
  - name: classify_complaint
    description: >
      Classify a single citizen complaint row. Reads the description and
      metadata, then returns category, priority, reason, and flag that
      exactly match the UC-0A classification schema.
    input: >
      dict with keys: complaint_id, date_raised, city, ward, location,
      description, reported_by, days_open
    output: >
      dict with keys: complaint_id, category, priority, reason, flag.
      Category is one of the 10 allowed strings. Priority is Urgent/Standard/Low
      based on severity keyword presence. Reason is one sentence citing specific
      words from description. Flag is NEEDS_REVIEW or blank.
    error_handling: >
      If the description is empty or missing, output category: Other,
      priority: Standard, reason: "No description provided", flag: NEEDS_REVIEW.
      If category is ambiguous, output category: Other and flag: NEEDS_REVIEW
      instead of guessing.

  - name: batch_classify
    description: >
      Read an input CSV of citizen complaints, apply classify_complaint to
      every row, and write a results CSV. Handles I/O errors gracefully.
    input: >
      input_path — path to CSV with columns: complaint_id, date_raised, city,
      ward, location, description, reported_by, days_open
    output: >
      output_path — CSV written with columns: complaint_id, category, priority,
      reason, flag. One row per input row.
    error_handling: >
      If the input file does not exist or cannot be read, raise a clear
      FileNotFoundError. If a specific row fails classification, produce a row
      with flag NEEDS_REVIEW and continue processing remaining rows — a single
      bad row must not crash the entire batch. Empty input files produce an
      empty output file with the correct header.
