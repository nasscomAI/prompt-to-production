# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies one complaint row into category, priority, reason, and flag per agents.md.
    input: A dict for one CSV row — must contain complaint_id and description; other fields are ignored for the decision.
    output: A dict with exactly the keys complaint_id, category, priority, reason, flag, in that order.
    decision_rule: >
      Scan description against the fixed keyword sets for the 10 categories.
      Exactly one match → that category. Zero matches → Other + NEEDS_REVIEW.
      Two or more distinct categories match → Other + NEEDS_REVIEW, reason
      names the tied categories. Independently, scan description against the
      severity keyword list — any hit forces priority Urgent regardless of
      category outcome.
    error_handling: >
      Missing or blank description → category Other, priority Standard, flag
      NEEDS_REVIEW, reason states the description was empty. Never raises,
      never drops the row.

  - name: batch_classify
    description: Reads the input CSV, calls classify_complaint on every row, writes the results CSV.
    input: Path to test_[city].csv (columns per data/city-test-files/*.csv).
    output: CSV at --output with header complaint_id,category,priority,reason,flag — one row per input row, same order.
    process_rule: Every input row produces exactly one output row. Rows are never merged, skipped, or reordered.
    error_handling: >
      A row that fails to parse still gets a row in the output — category
      Other, flag NEEDS_REVIEW, reason explains the parse failure — instead of
      crashing the whole batch or silently omitting the row.
