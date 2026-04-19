skills:
  - name: load_dataset
    input: A file path to the input CSV containing complaints (e.g., test_[city].csv).
    output: A parsed list or structured representation of complaint rows.
    error_handling: Aborts and raises an error if the input file cannot be read, is missing, or lacks the expected columns.

  - name: classify_complaint
    input: A single complaint description string.
    output: A structured record containing category, priority, a one-sentence reason, and an optional flag.
    error_handling: Sets the flag to NEEDS_REVIEW if genuinely ambiguous; fails if category deviates from exact allowed list.
