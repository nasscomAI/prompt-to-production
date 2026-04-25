# skills.md

skills:
  - name: classify_complaint
    description: Takes one complaint row in and extracts category, priority, reason, and flag out.
    input: A dictionary representing a single complaint row.
    output: A dictionary containing category, priority, reason, and flag.
    error_handling: Set flag to NEEDS_REVIEW when category is genuinely ambiguous.

  - name: batch_classify
    description: Reads input CSV, applies classify_complaint per row, writes output CSV.
    input: String input_path and string output_path.
    output: A CSV file written to output_path.
    error_handling: Must flag nulls, not crash on bad rows, and produce output even if some rows fail.
