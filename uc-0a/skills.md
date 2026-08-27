# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: >
      Classifies a single citizen complaint description into a structured
      record containing category, priority, reason, and an optional review flag.
    input: >
      One plain-text complaint description string (the content of a single CSV
      row's description field).
    output: >
      A structured record with four fields —
      category (exactly one of: Pothole, Flooding, Streetlight, Waste, Noise,
      Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other),
      priority (Urgent | Standard | Low),
      reason (one sentence citing specific words from the description),
      flag ("NEEDS_REVIEW" when category is genuinely ambiguous, otherwise blank).
    error_handling: >
      If the description is empty or contains no classifiable content, output
      category: Other, priority: Low, a reason stating the description was
      insufficient, and flag: NEEDS_REVIEW.
      If a severity keyword is present but the category is still ambiguous,
      set priority: Urgent and flag: NEEDS_REVIEW.

  - name: batch_classify
    description: >
      Reads an input CSV of citizen complaints (with the category and
      priority_flag columns stripped), applies classify_complaint to every row,
      and writes a fully classified output CSV.
    input: >
      File path to a CSV file (e.g. ../data/city-test-files/test_[city].csv)
      containing at minimum a description column; 15 rows per city dataset.
    output: >
      A CSV file written to uc-0a/results_[city].csv containing all original
      columns plus the four appended fields: category, priority, reason, flag.
    error_handling: >
      Rows where classify_complaint sets flag: NEEDS_REVIEW are written to the
      output as-is and are not skipped.
      Rows with a missing or empty description field are output with
      category: Other, priority: Low, reason: "Description field was empty.",
      flag: NEEDS_REVIEW.
      Any file-read or file-write error is surfaced immediately with the
      offending file path and row index; processing halts.
