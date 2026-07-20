skills:
  - name: classify_complaint
    description: >
      Classify a single citizen complaint dict into category, priority, reason,
      and flag according to the UC-0A schema.
    input: >
      dict with keys: complaint_id (str), description (str).
    output: >
      dict with keys: complaint_id, category, priority, reason, flag.
    error_handling: >
      If description is empty or missing, output category: Other, priority: Low,
      reason: "No description provided", flag: NEEDS_REVIEW. If category is
      ambiguous, output category: Other, flag: NEEDS_REVIEW.

  - name: batch_classify
    description: >
      Read an input CSV of complaints, apply classify_complaint to every row,
      and write the results to an output CSV.
    input: >
      input_path (str) — path to CSV with columns: complaint_id, description.
      output_path (str) — path to write the results CSV.
    output: >
      Writes a CSV with columns: complaint_id, category, priority, reason, flag.
      Returns None on success.
    error_handling: >
      Skips malformed rows with a warning, never crashes on bad input, and
      always produces the output file with valid rows. Null or blank
      descriptions get flag: NEEDS_REVIEW.
