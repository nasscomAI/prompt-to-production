skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and ambiguity flag.
    input: Dict with keys — id (str), description (str); category and priority_flag columns are stripped from input.
    output: Dict with keys — category (str), priority (str, one of Urgent/Standard/Low), reason (str), flag (str, NEEDS_REVIEW or empty).
    error_handling: If description is empty or unreadable, output category: Other, priority: Standard, reason: "Insufficient description to classify", flag: NEEDS_REVIEW. If ambiguous, set flag: NEEDS_REVIEW and output category: Other rather than guessing.

  - name: batch_classify
    description: Reads CSV input file, applies classify_complaint to each complaint row, writes classified results to output CSV.
    input: File path (str) to input CSV in ../data/city-test-files/test_[city].csv format; must include id and description columns.
    output: CSV file written to results_[city].csv with columns — id, description, category, priority, reason, flag. All rows processed; no partial failures.
    error_handling: If input file not found, raise FileNotFoundError. If a row fails classification (e.g. null description), log warning and set that row's category: Other, flag: NEEDS_REVIEW. If output path is unwritable, raise IOError.
