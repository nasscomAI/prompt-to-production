# skills.md

skills:
  - name: classify_complaint
    description: Classifies one citizen complaint into a fixed category and priority with a cited reason.
    input: One complaint row as a dict of strings (csv.DictReader row); needs `description`, passes through `complaint_id`.
    output: Dict — complaint_id (str), category (exact taxonomy string), priority (Urgent|Standard|Low), reason (one sentence), flag ("NEEDS_REVIEW" or "").
    error_handling: Missing/empty description → category Other, flag NEEDS_REVIEW, reason noting unreadable text; severity keywords matched case-insensitively; never raises on odd text.

  - name: batch_classify
    description: Reads a city CSV, applies classify_complaint to every row, writes the results CSV in input order.
    input: Path to test_[city].csv and output path for results_[city].csv.
    output: CSV with header complaint_id,category,priority,reason,flag — one row per input row.
    error_handling: Malformed rows (nulls, wrong column count) become Other/NEEDS_REVIEW rows instead of crashing; output file is always written even if some rows fail.
