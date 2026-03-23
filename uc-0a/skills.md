# skills.md
skills:
  - name: classify_complaint
    description: Classify single complaint row into schema category, priority, reason, flag.
    input: dict with 'description' key (str).
    output: dict {'category': str, 'priority': str, 'reason': str, 'flag': str or ''}.
    error_handling: If ambiguous, category='Other', flag='NEEDS_REVIEW', reason='Insufficient keywords'.

  - name: batch_classify
    description: Process full CSV input, apply classify_complaint per row, write output CSV.
    input: input_path (str), output_path (str).
    output: Writes CSV with original columns + category, priority, reason, flag.
    error_handling: Log bad rows, continue; never crash on single row failure.

