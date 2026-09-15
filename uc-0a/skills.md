skills:
  - name: classify_complaint
    description: >
      Classify a single citizen complaint into one of 10 categories,
      assign priority (Urgent if severity keywords present),
      write a one-sentence reason citing description words, and
      flag ambiguous cases with NEEDS_REVIEW.

    input: >
      dict with keys from input CSV row:
      complaint_id (str), date_raised (str), city (str), ward (str),
      location (str), description (str), reported_by (str), days_open (str)
      — category and priority_flag are stripped, do not expect them.

    output: >
      dict with exactly 5 keys:
      complaint_id (str) — passed through from input,
      category (str) — one of 10 allowed values only,
      priority (str) — Urgent | Standard | Low,
      reason (str) — exactly one sentence, must contain words from description,
      flag (str) — NEEDS_REVIEW or empty string

    enforcement:
      - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other"
      - "Priority must be Urgent if description contains any severity keyword: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse"
      - "Reason must be exactly one sentence citing specific words from the description"
      - "If no category matches clearly, output category: Other and flag: NEEDS_REVIEW"
      - "Never output a category not in the allowed list, never vary category strings"

    error_handling: >
      If description is missing or empty, return category: Other,
      priority: Standard, flag: NEEDS_REVIEW. Never crash on any input.

  - name: batch_classify
    description: >
      Read an input CSV of complaints (one row per complaint, headers as
      column names), apply classify_complaint to every row, and write a
      results CSV with complaint_id, category, priority, reason, flag.

    input: >
      input_path (str) — path to CSV with columns: complaint_id,
      date_raised, city, ward, location, description, reported_by, days_open
      output_path (str) — path for the results CSV

    output: >
      None — writes results CSV to output_path with columns:
      complaint_id, category, priority, reason, flag
      Headers and one row per input row, 15 rows expected per city file.

    error_handling: >
      Skips malformed rows with a warning printed to stdout.
      Always produces output for all valid rows. Never crashes on a
      single bad row. Uses UTF-8 encoding for both read and write.
