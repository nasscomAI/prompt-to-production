# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag.
    input: One complaint row (a mapping of column name to value) containing the description text.
    output: A mapping with exactly the keys category, priority, reason, and flag, matching the classification schema.
    error_handling: If the description is empty or the category is genuinely ambiguous, sets category to Other and flag to NEEDS_REVIEW.

  - name: batch_classify
    description: Reads an input CSV, applies classify_complaint to every row, and writes the output CSV.
    input: Path to an input CSV (../data/city-test-files/test_[city].csv) with category and priority_flag stripped.
    output: Writes results_[city].csv with one row per source row, appending category, priority, reason, and flag columns.
    error_handling: Rows that cannot be parsed are classified as Other with a NEEDS_REVIEW flag rather than being silently dropped.