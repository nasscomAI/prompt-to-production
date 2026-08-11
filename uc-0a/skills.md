# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies one complaint row into category, priority, a one-sentence reason and an optional NEEDS_REVIEW flag.
    input: dict with at least a 'description' field (string).
    output: dict with keys category (one of the 10 allowed strings), priority (Urgent/Standard/Low), reason (one sentence citing words from the description), flag (NEEDS_REVIEW or blank).
    error_handling: Missing or empty description returns category Other, priority Standard, flag NEEDS_REVIEW with an explanatory reason.

  - name: batch_classify
    description: Reads an input CSV, applies classify_complaint to every row, and writes the results CSV.
    input: input_path (string, path to test_[city].csv), output_path (string).
    output: writes results_[city].csv with columns complaint_id, category, priority, reason, flag.
    error_handling: Skips or flags rows that fail without crashing the batch; the output file is always written even if some rows fail.
