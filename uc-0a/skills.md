# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint into the fixed taxonomy with a priority, a cited reason, and an ambiguity flag.
    input: >
      One complaint row as a dict, e.g. {complaint_id, description, ...metadata}.
      The description is free text; category and priority_flag are absent and
      must be derived.
    output: >
      A dict with exactly: complaint_id, category, priority, reason, flag.
      - category: one of Pothole, Flooding, Streetlight, Waste, Noise, Road Damage,
        Heritage Damage, Heat Hazard, Drain Blockage, Other (verbatim).
      - priority: Urgent, Standard, or Low. Urgent whenever the description contains
        any severity keyword (injury, child, school, hospital, ambulance, fire,
        hazard, fell, collapse).
      - reason: one sentence quoting specific words from the description.
      - flag: NEEDS_REVIEW if the category is genuinely ambiguous, else blank.
    error_handling: >
      If no allowed category fits, return category: Other. If the complaint is too
      vague or fits two categories equally, set flag: NEEDS_REVIEW instead of
      guessing. If description is empty/null, return category: Other,
      priority: Standard, flag: NEEDS_REVIEW, and a reason noting the missing text.
      Never invent a category or fabricate words not in the description.

  - name: batch_classify
    description: Reads the input CSV, applies classify_complaint to every row, and writes the results CSV.
    input: >
      input_path (path to test_[city].csv, 15 rows) and output_path
      (path to results_[city].csv).
    output: >
      A CSV written to output_path with header
      complaint_id, category, priority, reason, flag — one row per input row,
      in the same order.
    error_handling: >
      Must not crash on a single bad or malformed row: catch per-row errors, still
      write that row with category: Other, flag: NEEDS_REVIEW, and a reason noting
      the failure, then continue. Flag null/empty fields rather than dropping rows.
      Always produce an output file even if some rows fail. Fail loudly only if the
      input file is missing or unreadable.
