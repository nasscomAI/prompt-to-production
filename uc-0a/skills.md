# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: >
      Assigns one civic complaint to exactly one allowed category and one
      allowed priority, and produces a quoted justification plus a review flag,
      using only that complaint's own description text.
    input: >
      A single dict representing one CSV row. Required keys: complaint_id (str),
      description (str). All other keys (ward, location, reported_by, days_open,
      date_raised, city) may be present but are deliberately ignored — they are
      not classification evidence.
    output: >
      A dict with exactly five keys, in this order:
      complaint_id (str, copied verbatim from input),
      category (str, one of the 10 allowed strings),
      priority (str, one of Urgent / Standard / Low),
      reason (str, one sentence containing at least one literal quoted fragment
      of the description),
      flag (str, either "NEEDS_REVIEW" or "").
    error_handling: >
      Missing or blank description → returns category "Other", priority
      "Standard", flag "NEEDS_REVIEW", reason "No description text supplied —
      cannot classify from row data alone." Missing complaint_id → substitutes
      "UNKNOWN" and flags NEEDS_REVIEW. Two or more competing categories →
      returns the primary one and flags NEEDS_REVIEW, naming the runner-up in
      the reason. Only weak/indirect evidence → returns the best match and flags
      NEEDS_REVIEW. Never raises; never returns a category outside the allowed
      list; never returns an empty reason.

  - name: batch_classify
    description: >
      Reads a city test CSV, applies classify_complaint to every row in file
      order, and writes a results CSV with one output row per input row.
    input: >
      input_path (str) — path to test_[city].csv with a header row containing at
      minimum complaint_id and description.
      output_path (str) — path to write the results CSV.
    output: >
      Writes a UTF-8 CSV with header complaint_id,category,priority,reason,flag
      and exactly as many data rows as the input had. Returns a summary dict:
      {total, urgent, standard, low, needs_review, failed_rows} for run-time
      verification against the input.
    error_handling: >
      Missing input file → raises FileNotFoundError with the attempted path
      before any output is written, so a half-written results file is never
      produced. Missing required header columns → raises ValueError naming the
      columns that were expected and the ones actually found. A row that raises
      during classification is caught, written out as category "Other",
      priority "Standard", flag "NEEDS_REVIEW" with the exception text in the
      reason, and counted in failed_rows — the run continues. Row count is
      asserted equal at the end; a mismatch is reported rather than passing
      silently.
