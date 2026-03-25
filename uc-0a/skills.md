# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into category,
      priority, reason, and flag according to the UC-0A schema.
    input: >
      dict — a single CSV row containing at minimum a `description` (str)
      field and a `complaint_id` (str) field.
    output: >
      dict with keys: complaint_id (str), category (str — one of:
      Pothole, Flooding, Streetlight, Waste, Noise, Road Damage,
      Heritage Damage, Heat Hazard, Drain Blockage, Other),
      priority (str — Urgent | Standard | Low),
      reason (str — one sentence citing description text),
      flag (str — NEEDS_REVIEW or empty string).
    error_handling: >
      If `description` is missing or empty, return category: Other,
      priority: Low, reason: "Description was empty or missing.",
      flag: NEEDS_REVIEW. Never raise an exception — always return a
      valid output dict so batch processing is not interrupted.

  - name: batch_classify
    description: Reads an input CSV of complaint rows, applies
      classify_complaint to every row, and writes a results CSV.
    input: >
      input_path (str) — path to a CSV file with `complaint_id` and
      `description` columns; output_path (str) — destination path for
      the results CSV.
    output: >
      Writes a CSV to output_path with columns: complaint_id, category,
      priority, reason, flag. Returns None.
    error_handling: >
      Malformed or unparseable rows are written with category: Other,
      priority: Low, a reason citing the parse error, and
      flag: NEEDS_REVIEW — processing continues for all remaining rows.
      If input_path cannot be opened, raise FileNotFoundError with a
      descriptive message before processing begins.
