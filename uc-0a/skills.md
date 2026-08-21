# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies one complaint row into category, priority, reason, and review flag.
    input: One dict with at least complaint_id (string) and description (string); may contain other CSV columns which are ignored.
    output: Dict with keys complaint_id, category (one of the 10 allowed exact strings), priority (Urgent/Standard/Low), reason (one sentence citing words from the description), flag ("NEEDS_REVIEW" or blank).
    error_handling: Missing or empty description returns category Other with NEEDS_REVIEW instead of crashing; a malformed row object is treated the same way; severity keywords always override to Urgent.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to every row, and writes the results CSV.
    input: input_path (string, path to test_[city].csv with header row), output_path (string, path for results_[city].csv).
    output: Results CSV with columns complaint_id, category, priority, reason, flag — one row per input row; returns the count of rows written.
    error_handling: A row that fails classification is written as Other + NEEDS_REVIEW with the failure noted in reason rather than aborting the batch; missing required columns, unreadable file, or wrong encoding exits with a clear error message on stderr and exit code 1.
