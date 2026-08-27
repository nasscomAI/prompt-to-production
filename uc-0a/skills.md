# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: >
      Classifies one citizen complaint row into category, priority, reason and flag.
    input: >
      A dict representing one CSV row, containing at least a description key and
      a complaint_id key.
    output: >
      A dict with keys: complaint_id, category, priority, reason, flag.
      category is one of the ten exact allowed strings; priority is Urgent,
      Standard or Low; reason is a single sentence citing specific words from
      the description; flag is blank or NEEDS_REVIEW.
    error_handling: >
      If the description is empty or missing, sets category to Other, priority
      to Standard, flag to NEEDS_REVIEW, and a reason noting no description was
      provided. Never crashes on malformed input.

  - name: batch_classify
    description: >
      Reads an input CSV, applies classify_complaint to every row, and writes
      the results CSV.
    input: >
      Paths: input_path to a test_[city].csv that has a header row, and
      output_path for the results file.
    output: >
      Writes results_[city].csv with columns complaint_id, category, priority,
      reason, flag — one row per successfully classified input row, in input
      order.
    error_handling: >
      Skips and flags bad rows instead of crashing; produces a partial output
      file even if some rows fail; the row count in the output matches the
      number of successfully classified rows.
