# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and review flag using the enforcement rules in agents.md.
    input: >
      dict with keys complaint_id, date_raised, city, ward, location,
      description, reported_by, days_open (description is the only field
      used for classification logic; the rest pass through / are used for
      geographic context in the reason text).
    output: >
      dict with keys complaint_id, category (one of the 10 allowed enum
      values), priority (Urgent/Standard/Low), reason (one sentence quoting
      the description), flag (NEEDS_REVIEW or empty string).
    error_handling: >
      If description is missing, blank, or unreadable, returns
      category="Other", priority="Low", flag="NEEDS_REVIEW", and a reason
      stating the description was empty — never raises, never skips the row.

  - name: batch_classify
    description: Reads the input CSV, applies classify_complaint to every row, and writes the results CSV — continuing past any single bad row instead of aborting the whole run.
    input: input_path (str, path to test_[city].csv), output_path (str, path to write results_[city].csv).
    output: >
      Writes output_path as a CSV with columns complaint_id, category,
      priority, reason, flag — one row per input row, same order. Returns
      None; prints a one-line summary count of Urgent/Standard/Low and
      NEEDS_REVIEW rows to stdout.
    error_handling: >
      If a row is missing required columns or classify_complaint raises,
      the row is still written with category="Other", priority="Low",
      flag="NEEDS_REVIEW", reason noting the row failed to parse — the
      batch never crashes and always produces an output row for every
      input row.
