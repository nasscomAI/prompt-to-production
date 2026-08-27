# skills.md
# UC-0A Complaint Classifier — two skills implement the RICE contract.

skills:
  - name: classify_complaint
    description: Classify one complaint row into category, priority, reason and flag using only the description text.
    input: dict with required keys complaint_id and description (string).
    output: dict with exactly complaint_id, category, priority, reason, flag.
    error_handling: Empty/missing description → category Other, flag NEEDS_REVIEW. Ambiguous description → category Other, flag NEEDS_REVIEW. Never invent categories outside taxonomy.

  - name: batch_classify
    description: Read a test_[city].csv, classify every row, and write results_[city].csv.
    input: paths input_csv and output_csv.
    output: CSV with header complaint_id, category, priority, reason, flag — one row per input.
    error_handling: Missing/unreadable input → exit with error message, no output file. Per-row failures are caught and skipped but still recorded so the output is produced even if rows fail.