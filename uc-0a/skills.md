# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classify a single citizen complaint row into the fixed 10-category taxonomy with severity-aware priority and cited justification.
    input: dict with keys complaint_id (str), description (str), optional ward/location/city (str) — description is primary signal
    output: dict with keys complaint_id (str), category (str ∈ allowed 10), priority (str ∈ Urgent|Standard|Low), reason (str — one sentence citing verbatim words from description), flag (str — NEEDS_REVIEW or blank)
    error_handling: If description is null/empty/whitespace or no taxonomy keywords match or two categories tie for top score, return category Other, reason citing the lack of signal or first words, and flag NEEDS_REVIEW; never throw; never hallucinate a category variation

  - name: batch_classify
    description: Read input CSV, apply classify_complaint per row, and write output CSV with robust per-row error isolation.
    input: input_path (str — path to test_[city].csv with headers complaint_id,date_raised,city,ward,location,description,reported_by,days_open), output_path (str — path to write results CSV)
    output: CSV file with header complaint_id,category,priority,reason,flag and one output row per input row (15 per city), written even if some rows fail
    error_handling: Flag nulls, wrap each row classification in try/except, on exception emit fallback row (category Other, priority Standard, reason describing error + citing description fragment, flag NEEDS_REVIEW), never crash whole batch, create output directory if missing
