# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies one citizen complaint row into a fixed-taxonomy category, a severity-aware priority, an audit-ready reason, and a review flag.
    input: >
      A dict for one CSV row with at least a `description` key (str) and a
      `days_open` key (str/int, may be missing or blank). Other columns
      (complaint_id, ward, location, reported_by, city, date_raised) may be
      present but MUST NOT influence the classification decision.
    output: >
      A dict with exactly five keys: complaint_id (str, passed through),
      category (str, one of the 10 allowed enum values), priority (str,
      Urgent/Standard/Low), reason (str, one sentence quoting the matched
      description text), flag (str, "NEEDS_REVIEW" or "").
    error_handling: >
      If description is missing/blank/unparseable, or an exception occurs
      during classification, the skill does not raise — it returns
      category: Other, priority: Standard, flag: NEEDS_REVIEW, and a reason
      stating what was missing (e.g. "description field was empty").
      If no category keyword matches, or matches conflict, it returns
      category: Other with flag: NEEDS_REVIEW rather than guessing.

  - name: batch_classify
    description: Reads an input complaints CSV, applies classify_complaint to every row, and writes a results CSV with the same rows plus the four classification columns appended.
    input: >
      input_path (str) — path to test_[city].csv with header
      complaint_id,date_raised,city,ward,location,description,reported_by,days_open.
      output_path (str) — path to write the results CSV.
    output: >
      Writes output_path: a CSV with every original input column PLUS
      category, priority, reason, flag appended, one output row per input
      row, in the same order. Returns nothing; prints a completion summary
      including counts of Urgent rows and NEEDS_REVIEW rows to stdout.
    error_handling: >
      If the input file is missing or unreadable, raises a clear
      FileNotFoundError-style message rather than a raw traceback. If the
      CSV is missing the `description` column entirely, raises before
      processing (this is a structural error, not a per-row error). A
      per-row failure (bad encoding in one field, unparseable days_open,
      etc.) is caught per-row so one bad row never prevents the rest of the
      file from being classified and written — the run must always produce
      an output file with one row per input row.
