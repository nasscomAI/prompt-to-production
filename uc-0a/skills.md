# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: >
      Classifies exactly one civic complaint row into a fixed category, an
      operational priority, an evidence-citing reason, and an ambiguity flag.
    input: >
      A single dict parsed from one CSV row, keyed by the input header names
      (complaint_id, date_raised, city, ward, location, description,
      reported_by, days_open). Only description is used for the decision;
      complaint_id is echoed to the output. All values are str; any value may
      be empty or None.
    output: >
      A dict with exactly five str keys — complaint_id, category, priority,
      reason, flag. category is one of the ten allowed strings; priority is one
      of Urgent, Standard, Low; reason is one sentence quoting at least one
      literal token from the description; flag is "NEEDS_REVIEW" or "".
    error_handling: >
      Never raises and never returns None — a row that cannot be classified is
      still a row that must be reported.
      Missing or empty description (missing justification failure mode):
      returns category Other, priority Standard, flag NEEDS_REVIEW, and a
      reason naming the empty field, rather than inventing a plausible
      category.
      Missing complaint_id: substitutes "UNKNOWN_ID" and flags NEEDS_REVIEW so
      the gap is visible downstream instead of silently indexing by position.
      Genuine ambiguity between two categories (false-confidence failure mode):
      returns the leading category with flag NEEDS_REVIEW whenever a rival
      category matched on comparable evidence — within one keyword hit — not
      only on an exact tie. A 2-to-1 keyword lead is still a judgement call,
      so it is surfaced rather than presented as certain.
      Zero category keyword matches (taxonomy-drift / hallucinated-sub-category
      failure mode): returns Other — it never mints a new category name to fit
      the text.
      Severity term present but category unresolved (severity-blindness failure
      mode): priority is still Urgent. The severity check is independent of the
      category check, so an unclassifiable injury complaint is never downgraded.

  - name: batch_classify
    description: >
      Reads an input complaints CSV, applies classify_complaint to every row in
      file order, and writes a results CSV with one output row per input row.
    input: >
      input_path (str) — path to test_[city].csv with a header row;
      output_path (str) — path to write results_[city].csv. Both are supplied
      from the CLI via --input and --output.
    output: >
      Writes a UTF-8 CSV with header complaint_id,category,priority,reason,flag
      and exactly one data row per input data row, in the original order.
      Returns a run summary dict with total_rows, urgent_count,
      needs_review_count, null_field_rows, and per_category counts, which is
      printed to stdout so the operator sees the shape of the run without
      opening the file.
    error_handling: >
      Missing input file or unreadable path: raises SystemExit with the offending
      path named, before any partial output file is created.
      Input missing the required description or complaint_id column: exits with
      an explicit message listing the columns actually found, rather than
      writing a full CSV of Other/NEEDS_REVIEW rows that looks like real work.
      Null or empty cells in any row: counted and reported in a null report
      printed before the results are written, so nulls are visible rather than
      silently coerced to empty strings.
      A row that raises any unexpected exception during classification: caught
      per row, written out as Other / Standard / NEEDS_REVIEW with the exception
      text in the reason, and the batch continues — one bad row never costs the
      other fourteen.
      Ragged rows (more or fewer fields than the header): processed on the
      fields that are present and flagged NEEDS_REVIEW.
