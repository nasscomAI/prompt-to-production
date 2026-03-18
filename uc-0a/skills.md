skills:
  - name: classify_complaint
    description: Classify one complaint row into category, priority, reason, and flag using only row content.
    input: A dictionary for one complaint row from the input CSV (with description and complaint_id).
    output: A dictionary with keys complaint_id, category, priority, reason, flag.
    error_handling: If the row is missing description or cannot be parsed, set category Other, priority Standard, reason with fallback text, and flag NEEDS_REVIEW.

  - name: batch_classify
    description: Read the input CSV, call classify_complaint for each row, and write the output CSV in required format.
    input: Input file path to test_[city].csv and output file path for results.
    output: A CSV file with columns complaint_id, category, priority, reason, flag.
    error_handling: Continue processing remaining rows even if one row fails; write fallback default classification for failed rows.
