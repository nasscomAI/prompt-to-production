# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: >
      Classifies a single citizen complaint row into an allowed category and priority,
      with a justification citing the complaint text and an optional review flag.
    input: >
      dict — one CSV row keyed by header name. Required keys: complaint_id (str),
      description (str). Other keys (date_raised, city, ward, location, reported_by,
      days_open) may be present but must be ignored for the classification decision.
    output: >
      dict with exactly five keys — complaint_id (str, copied from input),
      category (str, one of the ten allowed values), priority (str, one of Urgent,
      Standard, Low), reason (str, one sentence quoting at least one verbatim word or
      phrase from description), flag (str, either NEEDS_REVIEW or empty string).
    rules: >
      Priority is Urgent if description contains any of injury, child, school, hospital,
      ambulance, fire, hazard, fell, collapse (case-insensitive substring match); this
      overrides all other priority reasoning. Category is matched to the primary physical
      defect described, never to a consequence of it.
    error_handling: >
      Never raises and never returns None. Missing, empty, or whitespace-only description
      or complaint_id returns category: Other, priority: Standard, flag: NEEDS_REVIEW and
      a reason naming the missing field. Ambiguous description that fits two or more
      allowed categories equally returns the best-fit category with flag: NEEDS_REVIEW.
      Undeterminable category returns category: Other with flag: NEEDS_REVIEW rather than
      a guess. A missing complaint_id is emitted as an empty string, not fabricated.

  - name: batch_classify
    description: >
      Reads an input complaint CSV, applies classify_complaint to every row in order, and
      writes a results CSV containing one output row per input row.
    input: >
      input_path (str) — path to test_[city].csv, read as UTF-8 with newline="".
      output_path (str) — path to write the results CSV, written as UTF-8 with newline="".
    output: >
      None. Side effect: a CSV file at output_path with header
      complaint_id,category,priority,reason,flag and exactly as many data rows as the
      input, in input order. Prints a summary of rows processed and rows flagged.
    rules: >
      Row count in equals row count out. Row order is preserved. The header is written
      before any row is processed so a partial run still yields a readable file.
    error_handling: >
      A per-row exception is caught, logged to stderr with the complaint_id, and written
      as category: Other, priority: Standard, flag: NEEDS_REVIEW with a reason describing
      the failure — the batch continues. A missing or unreadable input file, or an input
      file lacking the description column, exits with a clear one-line message and a
      non-zero status instead of a traceback. An unwritable output path is reported the
      same way. The output file is produced even when every row fails.
