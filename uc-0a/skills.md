# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: >
      Classifies a single complaint row into the approved schema — one row in,
      category + priority + reason + flag out.
    input: >
      dict — one row from the input CSV (complaint_id, date_raised, city, ward,
      location, description, reported_by, days_open).
    output: >
      dict with keys: complaint_id, category, priority, reason, flag.
      category is one of the 10 allowed strings; priority is Urgent/Standard/Low;
      reason quotes words from the description; flag is NEEDS_REVIEW or empty string.
    error_handling: >
      If no severity keyword is present, priority is decided by description substance
      (Standard or Low). If the category is genuinely ambiguous, sets category to
      Other and flag to NEEDS_REVIEW instead of guessing. Never raises on missing fields —
      returns a row flagged NEEDS_REVIEW with reason explaining what was missing.

  - name: batch_classify
    description: >
      Reads the input CSV, applies classify_complaint to every row, and writes the
      results CSV with the same row count as the input.
    input: >
      input_path (str) — path to test_[city].csv; output_path (str) — path to write
      results_[city].csv.
    output: >
      Writes results_[city].csv containing one output row per input row, with columns:
      complaint_id, category, priority, reason, flag.
    error_handling: >
      Reports null or malformed rows as NEEDS_REVIEW instead of crashing; skips no rows;
      produces the output file even if some rows fail; raises a clear error only if the
      input file itself is missing or unreadable.
