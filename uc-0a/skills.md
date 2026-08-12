# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: >
      Classifies exactly one citizen complaint record into a fixed-enum service
      category and a response priority, and returns the evidence it used.
    input: >
      dict — one CSV row with keys complaint_id, date_raised, city, ward,
      location, description, reported_by, days_open. Only complaint_id and
      description are read; the rest are ignored by design. Keys may be absent
      and values may be empty strings.
    output: >
      dict with exactly five keys —
        complaint_id : str, echoed from input, or ROW_<n> if absent
        category     : str, one of the ten allowed schema strings
        priority     : str, one of Urgent, Standard, Low
        reason       : str, one sentence quoting the matched words from the
                       description
        flag         : str, NEEDS_REVIEW or empty string
    error_handling: >
      Never raises for content reasons. Missing or empty description returns
      category Other, priority Standard, flag NEEDS_REVIEW, and a reason naming
      the missing field. Missing complaint_id is substituted with a positional
      ROW_<n> identifier rather than dropped. No category signal returns Other
      with NEEDS_REVIEW rather than a guess. Weak or competing category
      evidence returns the best category with NEEDS_REVIEW rather than false
      confidence. Severity detection runs independently of category detection,
      so a row that is ambiguous about category is still correctly marked
      Urgent when a severity term is present.

  - name: batch_classify
    description: >
      Reads an input complaints CSV, applies classify_complaint to every row in
      file order, and writes the results CSV.
    input: >
      input_path : str — path to data/city-test-files/test_[city].csv
      output_path : str — path to write results_[city].csv
    output: >
      Writes a UTF-8 CSV with header complaint_id, category, priority, reason,
      flag and one row per input row, in input order. Returns a summary dict
      with rows_in, rows_out, urgent_count, needs_review_count and a per-
      category tally, which the CLI prints so the run is auditable without
      opening the file.
    error_handling: >
      Missing input file or unreadable path raises before any work is done,
      with the offending path in the message — this is a caller error, not a
      data error, and must fail loudly. A missing description column in the
      header is reported as a fatal schema error rather than silently producing
      15 Other rows. Per-row exceptions are caught, counted, and converted into
      an Other / NEEDS_REVIEW output row whose reason carries the exception
      text, so one bad row can never truncate the output file. rows_in must
      equal rows_out; if it does not, the CLI exits non-zero.
