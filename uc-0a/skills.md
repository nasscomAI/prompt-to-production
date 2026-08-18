skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag.
    input: "dict with keys from the complaint CSV row (at minimum: complaint_id, description); other fields (city, ward, location) may be used for context only."
    output: "dict with keys: complaint_id, category (one of the fixed 10-value enum), priority (Urgent/Standard/Low), reason (one sentence citing description text), flag (NEEDS_REVIEW or empty string)."
    error_handling: "If description is missing/empty, output category: Other, priority: Low, reason: 'No description provided', flag: NEEDS_REVIEW. Never raises on malformed input rows — always returns a row."

  - name: batch_classify
    description: Reads an input CSV of complaints, classifies every row with classify_complaint, and writes a results CSV.
    input: "input_path (str, path to test_[city].csv), output_path (str, path to write results_[city].csv)."
    output: "Writes output_path as CSV with columns: complaint_id, category, priority, reason, flag. Returns the count of rows written."
    error_handling: "Skips a row only if it has no complaint_id, logging a warning to stderr; still writes an output row for every other row even if classify_complaint's normal path fails, by falling back to category: Other, flag: NEEDS_REVIEW rather than crashing the batch."
