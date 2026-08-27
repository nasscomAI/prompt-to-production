# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: >
      Classify one citizen complaint row into category, priority, reason, and flag
      using the fixed UC-0A schema.
    input: >
      A single CSV row as a dict with at least complaint_id and description
      (other columns may be present but are not used for classification).
    output: >
      A dict with keys complaint_id (string), category (exact allowed string),
      priority (Urgent | Standard | Low), reason (one sentence citing description
      words), flag (NEEDS_REVIEW or empty string).
    error_handling: >
      If description is missing, empty, or non-informative: category=Other,
      priority=Low, reason notes the missing text, flag=NEEDS_REVIEW.
      If two allowed categories fit equally: category=Other, flag=NEEDS_REVIEW,
      reason cites the conflicting cues. If a severity keyword is present,
      priority is always Urgent regardless of category ambiguity. Never invent
      category names outside the allowed list.

  - name: batch_classify
    description: >
      Read an input complaints CSV, apply classify_complaint to every row, and
      write a results CSV.
    input: >
      input_path (string path to test_[city].csv) and output_path (string path
      for results_[city].csv). Input CSV has columns including complaint_id and
      description; category and priority_flag are absent.
    output: >
      A CSV at output_path with columns complaint_id, category, priority,
      reason, flag — one row per input row, same order as input.
    error_handling: >
      Do not crash the batch on a bad row: flag null/missing descriptions via
      classify_complaint, write a row with Other + NEEDS_REVIEW, and continue.
      If the input file is missing or unreadable, raise a clear error before
      writing output. Always produce an output file when the input opens,
      even if some rows fail classification.
