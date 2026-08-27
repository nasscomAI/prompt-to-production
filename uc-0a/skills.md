skills:
  - name: classify_complaint
    description: Classify a single complaint row to determine category, priority, reason, and flag.
    input: A single dictionary representing a complaint row (e.g. `{"complaint_id": "...", "description": "..."}`).
    output: A dictionary with keys `complaint_id`, `category`, `priority`, `reason`, and `flag`.
    error_handling: Return flag "NEEDS_REVIEW" and category "Other" if description is ambiguous or category cannot be uniquely determined.

  - name: batch_classify
    description: Read input CSV, apply `classify_complaint` to each row, and write the output CSV.
    input: Two strings representing `input_path` and `output_path`.
    output: None (writes a CSV file to `output_path`).
    error_handling: Log errors for bad rows but continue processing the rest. Do not crash on bad rows. Flag nulls appropriately.
