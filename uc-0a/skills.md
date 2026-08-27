# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single complaint into its correct taxonomy.
    input: one complaint row in (stripped of category and priority).
    output: category + priority + reason + flag out.
    error_handling: If the complaint description is genuinely ambiguous, set the flag to 'NEEDS_REVIEW' and assign to the best guess category or 'Other'.

  - name: batch_classify
    description: reads input CSV, applies classify_complaint per row, writes output CSV.
    input: File path to the input CSV (e.g., ../data/city-test-files/test_[your-city].csv).
    output: File path to the generated output CSV (e.g., uc-0a/results_[your-city].csv).
    error_handling: Skip the row and report an error if malformed, or assign 'NEEDS_REVIEW' flag.
