# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: >
      Classifies a single complaint row into category, priority, reason, and
      flag using deterministic keyword matching and the enforcement rules
      from agents.md.
    input: >
      A single dict with keys: complaint_id (str), description (str), plus
      other CSV columns (date_raised, city, ward, location, reported_by,
      days_open) which are preserved but not used for classification.
    output: >
      A dict with keys: complaint_id (str), category (str — one of the 10
      allowed values), priority (str — Urgent/Standard/Low), reason (str —
      one sentence citing complaint description words), flag (str —
      NEEDS_REVIEW or empty string).
    error_handling: >
      If the description is empty or missing, set category to Other, priority
      to Low, reason to "No description provided.", and flag to NEEDS_REVIEW.
      If no allowed category matches, set category to Other and flag to
      NEEDS_REVIEW. Never crash on a malformed row — always produce output.

  - name: batch_classify
    description: >
      Reads the input CSV, applies classify_complaint to every row, and
      writes the results to the output CSV with the schema:
      complaint_id, category, priority, reason, flag.
    input: >
      input_path (str — path to the test_[city].csv file) and output_path
      (str — path where results_[city].csv will be written).
    output: >
      A CSV file at output_path containing one header row plus one result
      row per input complaint. All input rows must be processed — none
      skipped silently.
    error_handling: >
      If a row fails to classify, write it to the output with category=Other,
      priority=Low, reason="Classification failed for this row.",
      flag=NEEDS_REVIEW. Report the count of failed rows to stderr.
      Never crash mid-batch — always produce a complete output file.
