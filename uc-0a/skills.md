skills:
  - name: classify_complaint
    description: >
      Classify a single complaint row into category, priority, reason, and flag
      by applying keyword-based rules from README.md to the description field.
    input: >
      dict with keys: complaint_id, description (string), and any other CSV
      columns (ignored).
    output: >
      dict with keys: complaint_id (passthrough), category (one of 10 allowed
      strings), priority (Urgent or Standard), reason (one sentence citing
      description words), flag (NEEDS_REVIEW or empty string).
    error_handling: >
      If description is empty or missing, set category=Other, priority=Standard,
      reason="No description provided", flag=NEEDS_REVIEW.

  - name: batch_classify
    description: >
      Read an input CSV of complaints, run classify_complaint on every row,
      and write the results CSV with columns: complaint_id, category, priority,
      reason, flag.
    input: >
      Two strings: input_path (path to CSV with complaint rows) and output_path
      (path to write results).
    output: >
      None (writes results CSV to output_path). Prints confirmation on success.
    error_handling: >
      Skips malformed rows with a warning instead of crashing. Always produces
      output CSV even if some rows fail. Missing columns raise a clear error.
