# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: >
      Classify a single citizen complaint row into schema-exact category,
      priority, reason, and flag.
    input: >
      dict — one complaint row with fields: complaint_id, date_raised, city,
      ward, location, description, reported_by, days_open.
    output: >
      dict — complaint_id, category, priority, reason, flag. Category is
      exactly one of the 10 schema values; priority is Urgent when a severity
      keyword is in the description, otherwise Standard; reason cites the
      specific words that drove the classification; flag is NEEDS_REVIEW when
      the category is genuinely ambiguous, otherwise blank.
    error_handling: >
      If the description is empty or unparseable, do not fabricate a
      classification — return reason "INVALID ROW" and flag NEEDS_REVIEW.
      If the category cannot be determined from the description alone, return
      category "Other" with flag NEEDS_REVIEW. Never invent categories outside
      the schema.

  - name: batch_classify
    description: >
      Read an input CSV of complaints, apply classify_complaint to every row,
      and write a results CSV with the classification columns added.
    input: >
      input_path — path to test_[city].csv (category and priority_flag columns
      already stripped); output_path — where results are written.
    output: >
      results CSV written to output_path, one row per input complaint, with
      columns complaint_id, category, priority, reason, flag.
    error_handling: >
      Bad or empty rows must never crash the batch — flag them (NEEDS_REVIEW /
      "INVALID ROW") and continue. Always produce an output file, even when
      some rows fail. Rows are written in input order, one classification per
      complaint.