# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: >
      Classifies a single citizen-complaint row into a fixed category and priority,
      with a quoted justification and an ambiguity flag, using the description text only.
    input: >
      dict — one CSV row. Required key: `description` (str, free text).
      Used for identity only: `complaint_id` (str).
      All other keys (city, ward, location, reported_by, days_open, date_raised)
      are ignored by contract and must not affect the result.
    output: >
      dict with exactly these 5 string keys, in this order:
        complaint_id — copied verbatim from input, or "UNKNOWN" if absent/blank
        category     — one of: Pothole | Flooding | Streetlight | Waste | Noise |
                       Road Damage | Heritage Damage | Heat Hazard | Drain Blockage | Other
        priority     — Urgent | Standard | Low
        reason       — one sentence quoting the literal matched word(s) from the description
        flag         — "NEEDS_REVIEW" or ""
      Pure function: same input dict always yields the same output dict.
    error_handling: >
      Never raises. Never guesses silently.
        - description missing / empty / not a string -> category Other, priority Standard,
          flag NEEDS_REVIEW, reason states the description was missing.
        - no category keyword matches -> category Other, flag NEEDS_REVIEW.
        - two or more categories tie on weight -> category chosen by the documented
          precedence order, flag NEEDS_REVIEW, reason names both competing categories.
        - only weak (secondary) keyword evidence, no strong keyword -> keep the category
          but flag NEEDS_REVIEW.
        - complaint_id missing -> "UNKNOWN" plus NEEDS_REVIEW.
      Severity keywords are evaluated independently of category, so an unclassifiable
      complaint that mentions injury/child/fire is still returned as Urgent.

  - name: batch_classify
    description: >
      Reads an input complaints CSV, applies classify_complaint to every row in file order,
      and writes a results CSV with one output row per input row.
    input: >
      input_path (str)  — path to data/city-test-files/test_[city].csv
      output_path (str) — path to write results_[city].csv
      Input file must be UTF-8 CSV with a header row containing a `description` column.
    output: >
      Writes CSV at output_path with header:
        complaint_id,category,priority,reason,flag
      Row count of output == row count of input, always, in the same order.
      Returns a summary dict of counts (total, urgent, standard, low, needs_review, failed)
      and prints it to stdout. Re-running on the same input rewrites an identical file.
    error_handling: >
      Fails loudly only on things that make the run meaningless; degrades gracefully otherwise.
        - input file missing/unreadable, or header has no `description` column ->
          print a clear message and exit non-zero WITHOUT writing a partial output file.
        - a single row raising any exception -> caught, written as
          Other / Standard / NEEDS_REVIEW with the error text in reason, counted in `failed`,
          and the batch continues. One bad row never kills the file.
        - short/ragged rows and null cells -> treated as empty strings, then flagged.
        - duplicate complaint_ids -> passed through unchanged (dedupe is not this agent's job)
          and reported in the summary.
        - output directory missing -> created before writing.
