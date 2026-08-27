skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag.
    input: "dict with keys complaint_id, description, location, days_open (strings/int, one CSV row)"
    output: "dict with keys complaint_id, category, priority, reason, flag"
    error_handling: >
      If description is empty or under 5 words, set category to Other, priority to Standard,
      reason to "Insufficient description to classify", and flag to NEEDS_REVIEW — never guess
      a specific category from missing information.

  - name: batch_classify
    description: Reads the input CSV, applies classify_complaint to every row, writes the output CSV.
    input: "input_path (str, path to test_[city].csv)"
    output: "output_path (str, path to results_[city].csv) — one output row per input row, same order"
    error_handling: >
      If a row is missing the description column entirely, still write an output row for it
      (category Other, flag NEEDS_REVIEW, reason stating the column was missing) rather than
      skipping the row or crashing the batch.
