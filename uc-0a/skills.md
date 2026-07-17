# skills.md

skills:
  - name: classify_complaint
    description: Classify one complaint row into category, priority, reason, and flag using strict UC-0A schema rules.
    input: "dict row containing complaint_id and complaint description text (description/complaint/details/message fallback)."
    output: "dict with keys: complaint_id, category, priority, reason, flag."
    error_handling: "If description is missing/blank or mapping is genuinely ambiguous, set category to Other, set flag to NEEDS_REVIEW, keep schema-valid priority, and still return a one-sentence reason."

  - name: batch_classify
    description: Read an input CSV, apply classify_complaint to each row, and write schema-valid output CSV without crashing on bad rows.
    input: "input_path: str to test_[city].csv and output_path: str for results_[city].csv."
    output: "CSV with columns: complaint_id, category, priority, reason, flag and one output row per input row."
    error_handling: "Handle row-level exceptions by writing fallback classification (Other, Standard, one-sentence reason, NEEDS_REVIEW) so processing continues and output is always produced."
