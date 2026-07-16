# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category + priority + reason + flag using keyword evidence from the description only.
    input: dict with keys complaint_id, description (plus other CSV columns, which are ignored for classification).
    output: dict with keys complaint_id, category (one of the 10 allowed strings), priority (Urgent/Standard/Low), reason (one sentence citing matched words), flag (NEEDS_REVIEW or blank).
    error_handling: Missing or empty description → category=Other, priority=Standard, flag=NEEDS_REVIEW, reason states no usable text. Multiple category keyword matches → best-scoring category plus flag=NEEDS_REVIEW.

  - name: batch_classify
    description: Reads the input CSV, applies classify_complaint to every row, and writes the results CSV.
    input: input_path (str, path to test_[city].csv), output_path (str, path for results CSV).
    output: results CSV with header complaint_id,category,priority,reason,flag — exactly one row per input row; returns count of rows written and count flagged.
    error_handling: Unreadable file → exits with a clear error message and no partial output. A row that raises during classification is written as Other/NEEDS_REVIEW instead of crashing the batch — output is always produced for every readable row.
