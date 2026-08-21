# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: One complaint row in → category + priority + reason + flag out.
    input: dict with at least `complaint_id` and `description` (UTF-8 CSV row); description may be empty or malformed.
    output: dict with keys complaint_id (str), category (one of the 10 exact taxonomy strings), priority (Urgent|Standard|Low), reason (one sentence quoting description words), flag ("NEEDS_REVIEW" or "").
    error_handling: empty/missing description → category Other, flag NEEDS_REVIEW, reason states description was absent; keyword ties → more-specific category kept plus flag NEEDS_REVIEW; unexpected exception inside scoring is impossible by construction (pure regex over lowercased text).

  - name: batch_classify
    description: Reads the input CSV, applies classify_complaint per row, writes results CSV with one row per input row.
    input: input_path to test_[city].csv (UTF-8, header row), output_path for results_[city].csv.
    output: writes CSV with header complaint_id,category,priority,reason,flag; prints counts of clean / NEEDS_REVIEW / skipped rows; returns None.
    error_handling: unreadable input or unwritable output → prints ERROR line and exits with code 1 without a traceback; any per-row exception is caught and emitted as an Other/NEEDS_REVIEW row so the batch always produces a complete output file.
