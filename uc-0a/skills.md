# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classify a single complaint row into category, priority, reason, and flag based on description text only
    input: dict with keys: complaint_id (str), description (str)
    output: dict with keys: complaint_id (str), category (str — one of 10 allowed), priority (str — Urgent/Standard/Low), reason (str — one sentence citing words from description), flag (str — "NEEDS_REVIEW" or "")
    error_handling: If description is empty or missing, return category: Other, priority: Low, reason: "No description provided", flag: NEEDS_REVIEW. If description yields multiple equally plausible categories, return category: Other, flag: NEEDS_REVIEW with reason explaining ambiguity.

  - name: batch_classify
    description: Read input CSV, apply classify_complaint to each row, write results CSV with error resilience
    input: input_path (str — path to test_[city].csv), output_path (str — path to write results_[city].csv)
    output: None (writes CSV file with columns: complaint_id, category, priority, reason, flag)
    error_handling: Skip rows with missing complaint_id or description (log warning). If classify_complaint raises exception, write row with category: Other, priority: Low, reason: "Classification error", flag: NEEDS_REVIEW. Continue processing remaining rows. Always produce output file even if some rows fail.