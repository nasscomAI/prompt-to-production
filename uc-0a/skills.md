skills:
  - name: classify_complaint
    description: Classify a single complaint row into `category`, `priority`, `reason`, and `flag`.
    input:
      type: object
      format: >
        A JSON object or CSV row containing at minimum a `description` string.
        Optional fields (id, location, timestamp, other metadata) may be present but will not be used for label values.
    output:
      type: object
      format: >
        A JSON object with keys:
        - category: one of [Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other]
        - priority: one of [Urgent, Standard, Low]
        - reason: one sentence that cites exact words from the input description
        - flag: either NEEDS_REVIEW or an empty string
    error_handling: >
      - If `description` is missing or not a string: return `category: Other`, `priority: Low`, `flag: NEEDS_REVIEW`, and `reason: "invalid input: missing description"`.
      - If the correct category is genuinely ambiguous: set `flag: NEEDS_REVIEW`, choose `category: Other` only if no allowed category clearly fits, and include a reason sentence quoting the ambiguous words.
      - If any severity keyword (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse) appears in `description`: set `priority: Urgent` (override any lower priority).
      - Never return category or priority values outside the allowed lists; when mapping is uncertain, prefer `flag: NEEDS_REVIEW` rather than inventing a new label.
      - Always provide a non-empty `reason` sentence quoting exact words from the description; do not return an empty reason.

  - name: batch_classify
    description: Read an input CSV of complaints, run `classify_complaint` for each row, and write a results CSV.
    input:
      type: object
      format: >
        A mapping with `input_path` (string path to CSV, e.g. ../data/city-test-files/test_<city>.csv) and `output_path` (string path to write results, must follow uc-0a/results_[your-city].csv convention when used in UC-0A).
        CSV rows must include a `description` column.
    output:
      type: object
      format: >
        Writes a CSV at `output_path` with columns: original input columns plus `category`, `priority`, `reason`, `flag`.
        Returns a summary object: { output_path: string, rows_processed: int, rows_flagged: int }.
    error_handling: >
      - For malformed CSV or missing file: abort with a clear error and do not write partial output; return an error message.
      - For a malformed row (missing/invalid description): include a result row with `category: Other`, `priority: Low`, `flag: NEEDS_REVIEW`, `reason: "invalid input: missing description"` and continue processing remaining rows.
      - For rows where `classify_complaint` sets `flag: NEEDS_REVIEW`: include them in the output unchanged and increment `rows_flagged`; also write a short diagnostics log entry with row id/index and reason.
      - Detect and record potential failure modes (taxonomy drift, severity blindness, missing justification, hallucinated sub-categories, false high-confidence on ambiguous rows) by flagging affected rows with `NEEDS_REVIEW` and including a diagnostic summary in the return value.