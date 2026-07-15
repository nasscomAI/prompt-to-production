# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies one complaint row into category + priority + reason + flag.
    input: >
      A dict for one complaint row with at least complaint_id and description
      (city/ward/location optional).
    output: >
      A dict with keys complaint_id, category, priority, reason, flag. category is
      one of the 10 allowed values; priority is Urgent or Standard; reason is one
      sentence citing description words; flag is NEEDS_REVIEW or "".
    error_handling: >
      Empty/null description → category Other, priority Standard, flag NEEDS_REVIEW.
      No category match → Other + NEEDS_REVIEW. Multiple category matches → primary
      category + NEEDS_REVIEW. Never raises for well-formed row dicts.

  - name: batch_classify
    description: Reads the input CSV, applies classify_complaint per row, writes results CSV.
    input: input_path (test_[city].csv) and output_path for the results CSV.
    output: >
      A results CSV with header complaint_id,category,priority,reason,flag and one
      row per input row. Prints a summary count (Urgent / NEEDS_REVIEW / failed).
    error_handling: >
      Each row is classified inside try/except so a single malformed row is captured,
      flagged NEEDS_REVIEW, and never aborts the batch. Output is always written.
