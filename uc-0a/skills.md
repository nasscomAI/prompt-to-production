# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: >
      Classifies exactly one civic complaint into a fixed-taxonomy category,
      a priority level, a citation-bearing reason, and an ambiguity flag.
    input: >
      dict — one CSV row. Reads only `complaint_id` (str) and `description`
      (str). All other columns (ward, days_open, reported_by, location, city,
      date_raised) are present but deliberately ignored.
    output: >
      dict with exactly five keys, all str:
        complaint_id — echoed from input
        category     — one of the 10 allowed taxonomy strings
        priority     — "Urgent" | "Standard" | "Low"
        reason       — one sentence, contains >=1 verbatim term from description
        flag         — "NEEDS_REVIEW" or "" (empty string, not None)
    error_handling: >
      Never raises. Blank/missing description or missing complaint_id ->
      category "Other", priority "Standard", flag "NEEDS_REVIEW", and a reason
      that names the missing field. Two categories tied on evidence ->
      alphabetically first tied category + NEEDS_REVIEW, both names in reason.
      Zero keyword evidence -> "Other" + NEEDS_REVIEW. It never guesses and
      never returns a category outside the allowed 10.

  - name: batch_classify
    description: >
      Reads an input complaints CSV, applies classify_complaint to every row in
      file order, and writes a results CSV with a stable 5-column header.
    input: >
      input_path (str) — path to test_[city].csv, UTF-8, with a header row
      containing at least `complaint_id` and `description`.
      output_path (str) — path to write the results CSV.
    output: >
      Writes UTF-8 CSV with header complaint_id,category,priority,reason,flag —
      exactly one data row per input data row, in input order. Returns a summary
      dict (total, urgent, needs_review, failed) and prints a triage summary plus
      a null/blank-field report to stdout before writing.
    error_handling: >
      Missing input file or unreadable CSV -> single clear error message, exit
      code 1, no partial output file. A row that raises for any unforeseen
      reason is caught individually and emitted as category "Other", priority
      "Standard", flag "NEEDS_REVIEW" with the exception text in the reason —
      so one bad row can never abort the batch. Output is always produced even
      if some rows fail, and the input/output row counts are asserted equal
      before the run is reported as clean.
