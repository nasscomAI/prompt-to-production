# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies one complaint row into a schema-valid category, priority, one-sentence reason and an optional NEEDS_REVIEW flag.
    input: >
      dict — one CSV row with keys complaint_id, date_raised, city, ward,
      location, description, reported_by, days_open; any key except
      complaint_id may be missing or null.
    output: >
      dict — { complaint_id: str,
               category: one of Pothole | Flooding | Streetlight | Waste |
                         Noise | Road Damage | Heritage Damage | Heat Hazard |
                         Drain Blockage | Other (exact strings),
               priority: Urgent | Standard | Low,
               reason: str (one sentence quoting words from description),
               flag: "NEEDS_REVIEW" or "" }.
    error_handling: >
      If the description is empty/null or no category fits it, return
      category: Other, priority: Standard, flag: NEEDS_REVIEW — never raise,
      never leave a field blank. If two categories fit equally well, return
      category: Other with flag: NEEDS_REVIEW instead of guessing.

  - name: batch_classify
    description: Reads a city test CSV, applies classify_complaint to every row and writes the results CSV without crashing on bad rows.
    input: >
      Two paths — input_path to a test_[city].csv file (15 rows, header:
      complaint_id,date_raised,city,ward,location,description,reported_by,days_open)
      and output_path for results_[city].csv.
    output: >
      Writes results CSV with header
      complaint_id,category,priority,reason,flag — exactly one output row per
      readable input row; prints a summary (total, classified, flagged) to stdout.
    error_handling: >
      Rows with null/missing cells are still classified via classify_complaint's
      refusal fallback rather than skipped or crashed. Malformed CSV lines are
      logged to stderr and skipped. The output file is always written if the
      input can be opened; exits non-zero only when the input file cannot be read.
