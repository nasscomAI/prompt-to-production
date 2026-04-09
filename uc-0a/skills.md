# skills.md

skills:
  - name: classify_complaint
    description: Classify a single complaint row by mapping its description to a Category, Priority, Reason, and Flag.
    input: Dictionary representing a single complaint row with keys like `complaint_id`, `description`, etc.
    output: Dictionary with the resulting schema fields: `category`, `priority`, `reason`, and `flag` (along with `complaint_id`).
    error_handling: If standard mapping rules fail or input is unparseable/ambiguous, default category to "Other" and set flag to "NEEDS_REVIEW". Return the safest default schema to prevent pipeline failure.

  - name: batch_classify
    description: Read input CSV, applies classify_complaint sequentially per row, and writes to an output CSV.
    input: `input_path` (string, path to input CSV) and `output_path` (string, path to output CSV).
    output: Writes a formatted CSV file to the `output_path`. Returns None.
    error_handling: Gracefully skips rows that crash parsing, flags null inputs, and ensures output CSV generation completes even with some row failures.
