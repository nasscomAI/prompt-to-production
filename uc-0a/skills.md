# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag.
    input: dict — one CSV row with keys complaint_id, date_raised, city, ward, location, description, reported_by, days_open; description is the primary classification signal.
    output: dict with keys complaint_id (str), category (str — one of Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other), priority (str — Urgent, Standard, or Low), reason (str — one sentence citing specific words from the description), flag (str — "NEEDS_REVIEW" or blank).
    error_handling: If description is missing, null, or unreadable → category Other, priority Standard, reason stating the description was unusable, flag NEEDS_REVIEW. If the row is genuinely ambiguous between allowed categories → choose Other (or closest defensible category) and set flag NEEDS_REVIEW rather than inventing a category name. Severity keywords always force priority Urgent before any other logic.

  - name: batch_classify
    description: Reads the input CSV, applies classify_complaint to every row, and writes the results CSV.
    input: two strings — input_path (test_[city].csv) and output_path (results_[city].csv), as passed via --input/--output CLI arguments.
    output: None returned — writes results_[city].csv with header complaint_id,category,priority,reason,flag and exactly one output row per input row, then prints completion status.
    error_handling: Missing or unreadable input file → exit early with a clear error message and do not write an output file. A bad individual row never aborts the batch — it is classified via the error path of classify_complaint (Other + NEEDS_REVIEW) and processing continues. The output file is always produced for all successfully read rows.
