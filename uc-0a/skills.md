skills:
  - name: classify_complaint
    description: Takes one complaint row and returns category, priority, reason, and flag based strictly on the description text.
    input: Dict with keys complaint_id and description (strings).
    output: Dict with keys complaint_id, category, priority, reason, flag.
    error_handling: If description is empty or missing, set category to Other, priority to Low, reason to "Description missing — cannot classify", flag to NEEDS_REVIEW.

  - name: batch_classify
    description: Reads the input CSV row by row, applies classify_complaint to each row, and writes all results to the output CSV.
    input: input_path (string path to test_[city].csv), output_path (string path for results CSV).
    output: CSV file with columns complaint_id, category, priority, reason, flag — one row per input complaint.
    error_handling: If a row cannot be processed, write the complaint_id with category Other, priority Low, reason describing the error, and flag NEEDS_REVIEW — never skip a row silently.
