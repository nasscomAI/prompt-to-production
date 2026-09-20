skills:
  - name: classify_complaint
    description: Classifies one citizen complaint row into a fixed category, priority, reason, and ambiguity flag.
    input: "A single CSV row as a dict with fields: complaint_id, date_raised, city, ward, location, description, reported_by, days_open."
    output: "A dict with keys complaint_id (string), category (one allowed taxonomy string), priority (Urgent | Standard | Low), reason (one sentence citing description words), flag (NEEDS_REVIEW or empty string)."
    error_handling: "If description is missing or blank, return category Other, priority Standard, reason stating the description is missing, flag NEEDS_REVIEW. If two categories score equally, pick the primary match and set flag NEEDS_REVIEW. If no category keyword matches, return Other with flag NEEDS_REVIEW. Never invent a category name outside the allowed list."

  - name: batch_classify
    description: Reads the city test CSV, applies classify_complaint to every row, and writes results_[city].csv.
    input: "input_path (string path to test_[city].csv) and output_path (string path to results CSV)."
    output: "A CSV file with header complaint_id,category,priority,reason,flag and one row per input complaint. Script still writes output if some rows fail."
    error_handling: "Skip crashing on a bad row: record that row as category Other, priority Standard, reason citing the parse error, flag NEEDS_REVIEW, then continue. Missing file raises a clear error and does not write a partial silent result. Null or empty descriptions are flagged, never dropped."
