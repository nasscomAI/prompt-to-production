skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint description into a category, priority, reason, and ambiguity flag according to the fixed schema.
    input:
      type: object
      format: >
        A single CSV row represented as a key-value map with at minimum a
        plain-text complaint description field (string, non-empty).
    output:
      type: object
      format: >
        A key-value map with four fields:
        category (string — exactly one of: Pothole, Flooding, Streetlight, Waste,
        Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other);
        priority (string — one of: Urgent, Standard, Low);
        reason (string — one sentence quoting specific words from the description);
        flag (string — NEEDS_REVIEW or empty string).
    error_handling: >
      If the description is empty or missing, set category to Other, priority to
      Standard, reason to "Description was empty or missing — cannot classify.",
      and flag to NEEDS_REVIEW.
      If the description is present but does not match any specific category with
      confidence, set category to Other, flag to NEEDS_REVIEW, and reason must still
      cite the words that made classification ambiguous.
      The skill must never raise an exception or return a partial row — all four
      output fields are always populated.

  - name: batch_classify
    description: Reads an input CSV of complaint rows, applies classify_complaint to each row, and writes the enriched results to an output CSV.
    input:
      type: file
      format: >
        A UTF-8 CSV file at the path supplied via --input; must contain at least a
        complaint description column; category and priority_flag columns are absent
        (stripped before delivery). Minimum 1 row, expected 15 rows per city file.
    output:
      type: file
      format: >
        A UTF-8 CSV file written to the path supplied via --output containing all
        original columns plus four appended columns: category, priority, reason, flag.
        Row count must equal input row count exactly — no rows added or dropped.
    error_handling: >
      If the input file is not found or cannot be parsed as CSV, abort immediately
      with a non-zero exit code and print the file path and error to stderr — do not
      write a partial output file.
      If an individual row fails classification, apply the classify_complaint
      error-handling rules for that row (category Other, flag NEEDS_REVIEW) and
      continue processing remaining rows — a single bad row must not abort the batch.
      If the output path is not writable, abort with a non-zero exit code and print
      the path and error to stderr before any rows are written.
