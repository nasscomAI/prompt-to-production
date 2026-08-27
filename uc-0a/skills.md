skills:
  - name: classify_complaint
    description: Classifies a single civic complaint row into category, priority, reason, and flag based on RICE enforcement rules.
    input: >
      A dict representing one CSV row with keys:
        complaint_id (str), description (str).
      All other fields (ward, location, etc.) are available but must NOT be used for classification.
    output: >
      A dict with keys:
        complaint_id (str) — copied verbatim from input,
        category (str) — exactly one of: Pothole · Flooding · Streetlight · Waste · Noise · Road Damage · Heritage Damage · Heat Hazard · Drain Blockage · Other,
        priority (str) — one of: Urgent / Standard / Low,
        reason (str) — one sentence citing specific words from the description,
        flag (str) — "NEEDS_REVIEW" or blank string.
    error_handling: >
      If description is empty or None, set category to Other, priority to Low,
      reason to "No description provided — cannot classify", flag to "NEEDS_REVIEW".
      Never raise an exception; always return a valid output dict.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes a results CSV.
    input: >
      input_path (str) — path to test_[city].csv,
      output_path (str) — path to write results_[city].csv.
      Input CSV must have columns: complaint_id, description (others may be present and are passed through).
    output: >
      Writes a CSV at output_path with columns:
        complaint_id, category, priority, reason, flag.
      Also prints a summary: total rows processed, Urgent count, NEEDS_REVIEW count, any rows that failed.
    error_handling: >
      If a row fails classification (unexpected exception), log the complaint_id and error,
      write that row with category=Other, priority=Low, reason="Classification error", flag="NEEDS_REVIEW",
      and continue processing remaining rows. Never abort the entire batch for a single bad row.
