# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: >
      Classifies a single complaint row into category + priority + reason + flag.
    input: >
      dict with key complaint_id (str) and key description (str, free text).
    output: >
      dict with keys: complaint_id, category, priority, reason, flag.
      category is one of the 10 allowed strings; flag is NEEDS_REVIEW or empty.
    error_handling: >
      Returns category: Other and flag: NEEDS_REVIEW when the description is too
      ambiguous to classify; sets priority: Urgent whenever a severity keyword is
      found; leaves flag empty otherwise.

  - name: batch_classify
    description: >
      Reads an input complaint CSV, applies classify_complaint to every row, and
      writes the results CSV.
    input: >
      Path to test_[city].csv with columns including complaint_id and description;
      path for the output CSV.
    output: >
      results_[city].csv with one row per input row: complaint_id, category,
      priority, reason, flag.
    error_handling: >
      Never crashes on malformed rows — invalid rows are skipped and flagged in
      the output with NEEDS_REVIEW; a results file is produced even if some rows fail.