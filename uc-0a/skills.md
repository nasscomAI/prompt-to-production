# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into an operational category, priority, one-sentence justification, and ambiguity flag.
    input: >
      One complaint row as a dict with keys: complaint_id, date_raised, city,
      ward, location, description, reported_by, days_open (string values from
      the input CSV). Only `description` drives classification; other fields
      are passthrough.
    output: >
      A dict with keys: complaint_id (copied verbatim), category (exactly one
      of Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage
      Damage, Heat Hazard, Drain Blockage, Other), priority (Urgent |
      Standard | Low), reason (one sentence quoting words present verbatim in
      the description), flag (NEEDS_REVIEW or empty string).
    error_handling: >
      If description is missing, empty, unreadable, or supports no taxonomy
      category, return category=Other, flag=NEEDS_REVIEW, and a reason naming
      what information is missing. Never raise an unhandled exception; never
      invent sub-categories; severity keywords in the description always force
      priority=Urgent.

  - name: batch_classify
    description: Reads the input complaints CSV, applies classify_complaint to every row, and writes the results CSV.
    input: >
      Paths to input CSV (test_[city].csv with columns complaint_id,
      date_raised, city, ward, location, description, reported_by,
      days_open) and output CSV path.
    output: >
      Writes results CSV with one row per input row — never fewer — with
      columns: complaint_id, category, priority, reason, flag.
    error_handling: >
      Malformed rows (missing fields, bad encoding) are still written to the
      output with category=Other, flag=NEEDS_REVIEW rather than crashing or
      being skipped. Zero-row drop policy: every input complaint_id must
      appear exactly once in the output even if individual rows fail.
