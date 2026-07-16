# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: >
      Classifies a single complaint row into category, priority, reason, and
      flag, applying the fixed schema and severity keyword rules from agents.md.
    input: >
      A dict representing one CSV row, containing at least the keys
      `complaint_id` and `description`. Other columns (ward, location, date,
      reported_by, days_open) may be present but are ignored for classification.
    output: >
      A dict with exactly these keys:
      complaint_id (str, copied from input),
      category (str, one of the 10 allowed values),
      priority (str, one of Urgent / Standard / Low),
      reason (str, one sentence citing words from the description),
      flag (str, "NEEDS_REVIEW" or "").
    error_handling: >
      If `description` is empty or missing, return category="Other",
      priority="Standard", a reason noting the missing description, and
      flag="NEEDS_REVIEW". If the complaint type is genuinely ambiguous, return
      category="Other" with flag="NEEDS_REVIEW". Never raise on a single bad row.

  - name: batch_classify
    description: >
      Reads an input CSV of complaints, applies classify_complaint to every row,
      and writes a results CSV. Produces output even when some rows fail.
    input: >
      input_path (str) — path to test_[city].csv;
      output_path (str) — path to write the results CSV.
    output: >
      Writes a CSV to output_path with header
      complaint_id,category,priority,reason,flag and one row per input row.
      Returns None (side effect is the written file).
    error_handling: >
      Rows that are null or malformed are flagged NEEDS_REVIEW rather than
      dropped, so every input row yields exactly one output row. Never crashes on
      a bad row — a per-row failure is caught, logged, and written as an Other /
      NEEDS_REVIEW result. If the input file cannot be opened, fail fast with a
      clear error message before any output is written.
