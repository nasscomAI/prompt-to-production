skills:
  - name: classify_complaint
    description: >
      Classifies a single complaint row into category, priority, reason, and
      flag using keyword-based rules defined in the classification schema.
    input: >
      dict — a single row from the input CSV with a 'description' key
    output: >
      dict — keys: complaint_id, category (from allowed list), priority
      (Urgent/Standard/Low), reason (one sentence citing description words),
      flag (NEEDS_REVIEW or blank)
    error_handling: >
      If description is missing or empty, returns category: Other, flag:
      NEEDS_REVIEW. If the input dict lacks a complaint_id, uses 'UNKNOWN'.
      Never crashes — catches all exceptions and writes an error row with
      NEEDS_REVIEW.

  - name: batch_classify
    description: >
      Reads an input CSV of complaint rows, applies classify_complaint to each
      row, and writes the results to an output CSV with columns:
      complaint_id, category, priority, reason, flag.
    input: >
      input_path (str) — path to test_[city].csv; output_path (str) — path
      for results CSV
    output: >
      A CSV file written to output_path with all required columns. Prints
      confirmation to stdout.
    error_handling: >
      Creates the output directory if it does not exist. If a single row fails
      classification, writes that row with Other/Standard/NEEDS_REVIEW and
      continues processing remaining rows. Uses utf-8-sig encoding for input
      and utf-8 for output.
