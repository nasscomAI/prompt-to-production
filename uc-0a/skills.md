skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into an exact taxonomy category by scoring its curated root-term maps over the description text (strong=2, weak=1), computing priority from the severity/caution/Low model, composing a one-sentence evidence-quoting reason, and setting the NEEDS_REVIEW flag only for genuinely ambiguous or out-of-taxonomy cases.
    input: A dictionary representing one CSV row with 'complaint_id' and 'description' (other fields such as 'city', 'ward', 'location', 'reported_by', 'days_open' are not used for classification).
    output: A dictionary with keys 'complaint_id' (str, preserved from input), 'category' (str, one of the 10 allowed values), 'priority' (str: Urgent/Standard/Low), 'reason' (str: single sentence quoting matched evidence terms), and 'flag' (str: 'NEEDS_REVIEW' or empty).
    error_handling: Empty, corrupted, or genuinely ambiguous descriptions yield 'Other' + 'Standard' (or severity-based priority when the missing-text row still trips a severity signal) + 'NEEDS_REVIEW', with a reason stating why; never crashes.

  - name: validate_result
    description: Checks a classified row against the full enforcement contract (schema membership, Urgent-IFF-severity bijection, evidence citation present in the row's own description, NEEDS_REVIEW only when ambiguous, preserved complaint_id) and returns the list of violations.
    input: classified_row (dict) and its source description (str).
    output: A list of violation strings; an empty list means the row is compliant.
    error_handling: No side effects; every check is reported as a string so the caller can decide the batch outcome.

  - name: batch_classify
    description: Reads the input CSV, classifies every row with classify_complaint, runs validate_result on every row, and writes the results CSV only when the ENTIRE batch is compliant (row count equal as well). Prints a summary of category/priority/flag counts on success.
    input: input_path (str) and output_path (str).
    output: UTF-8 CSV with header [complaint_id, category, priority, reason, flag]; raises SystemExit(1) after printing all violations to stderr and does NOT write any file when validation fails.
    error_handling: Missing input file raises FileNotFoundError; creating the output directory happens only after validation passes, so a failed batch leaves no partial artifact.

  - name: run_self_check
    description: Non-destructive verification that classifies all four known city test files (ahmedabad, pune, hyderabad, kolkata) in memory and confirms every row passes validate_result and the expected row counts, printing per-city PASS/FAIL and returning a failure count.
    input: None (uses the known ../data/city-test-files paths).
    output: Prints a per-city PASS/FAIL summary plus overall exit-code semantics (0 = all pass, others = failure count).
    error_handling: A missing fixture file is reported as FAIL for that city rather than crashing.