# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint description into category, priority, reason, and flag using the fixed schema and severity keywords.
    input: dict — one complaint row containing a complaint description string.
    output: dict — {category, priority, reason, flag} where category is one of the 10 allowed strings, priority is Urgent/Standard/Low, reason is a one-sentence citation, and flag is NEEDS_REVIEW or blank.
    error_handling: If the description is empty or the category is genuinely ambiguous, returns category: Other, priority: Low, flag: NEEDS_REVIEW with a reason explaining why, rather than guessing.

  - name: batch_classify
    description: Reads the city test CSV, applies classify_complaint to every row, and writes the results CSV with one classified row per input row.
    input: str — path to the input CSV (test_[city].csv); str — path to the output CSV (results_[city].csv).
    output: CSV file — every input row preserved plus category, priority, reason, and flag columns.
    error_handling: If the input file is missing or columns are wrong, raises a clear error. Ambiguous rows are still written with flag set to NEEDS_REVIEW — never skipped or guessed.