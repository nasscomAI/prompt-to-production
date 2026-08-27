# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: >
      Classifies a single complaint row into a fixed-taxonomy category with a
      priority level, a one-sentence cited reason, and an ambiguity flag.
    input: >
      One dict — a single complaint row containing at minimum `complaint_id`
      (str) and `description` (str; may be empty or null).
    output: >
      One dict with exactly five keys — complaint_id (str, passed through),
      category (one of: Pothole, Flooding, Streetlight, Waste, Noise,
      Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other),
      priority (Urgent | Standard | Low), reason (str, one sentence quoting
      words from the description), flag (NEEDS_REVIEW or "").
    error_handling: >
      Empty, whitespace-only, or missing description returns category "Other",
      priority "Standard", a reason stating no usable detail was provided, and
      flag "NEEDS_REVIEW". If the description is genuinely ambiguous between two
      or more categories, returns "Other" with flag "NEEDS_REVIEW" instead of a
      confident guess. Never raises on bad row values; always returns all five
      fields populated.

  - name: batch_classify
    description: >
      Reads a complaints CSV, applies classify_complaint to every row, and
      writes a results CSV preserving input order.
    input: >
      Two strings — `input_path` to a UTF-8 CSV with header row (the
      test_[city].csv format) and `output_path` for the results CSV.
    output: >
      Writes a results CSV with columns: complaint_id, category, priority,
      reason, flag — one row per input row, same order. Prints a one-line
      summary (rows processed / flagged). Returns None.
    error_handling: >
      Rows with null or missing fields are classified and flagged
      (NEEDS_REVIEW), never dropped. Malformed rows (wrong column count,
      unparseable values) are written as category "Other" with flag
      "NEEDS_REVIEW" so output row count always equals input row count. The
      script never crashes mid-file: even if some rows fail, a complete output
      file is produced. An unreadable or missing input file fails fast with a
      clear error message before any output is written.
