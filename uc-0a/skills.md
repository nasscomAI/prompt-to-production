# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: >
      Classifies a single citizen complaint row into category, priority, reason,
      and flag using only the description field and the enforcement rules in agents.md.
    input: >
      A Python dict representing one CSV row with at least a `description` key
      (string). The `complaint_id` key is also expected and passed through to output.
    output: >
      A Python dict with five keys:
        complaint_id (string, passed through from input),
        category     (string, one of the 10 allowed values),
        priority     (string: "Urgent" | "Standard" | "Low"),
        reason       (string, one sentence citing words from the description),
        flag         (string: "NEEDS_REVIEW" | "" — empty string when not flagged).
    error_handling: >
      If `description` is missing, empty, or None, return category "Other",
      priority "Low", reason "Description insufficient to classify.", flag
      "NEEDS_REVIEW". Never raise an exception — always return a dict.

  - name: batch_classify
    description: >
      Reads an input CSV of complaint rows, applies classify_complaint to every row,
      and writes the results to an output CSV. Tolerates bad rows without crashing.
    input: >
      Two strings: input_path (path to a CSV file with columns including
      complaint_id and description) and output_path (path where the results
      CSV will be written).
    output: >
      A CSV file at output_path with columns:
        complaint_id, category, priority, reason, flag.
      One row per input row. Rows that fail classification contain "ERROR" in
      category, blank priority and reason, and "NEEDS_REVIEW" in flag.
    error_handling: >
      If a row raises any exception during classification, catch the exception,
      log a warning to stderr, write an ERROR row for that complaint_id, and
      continue processing remaining rows. If the input file does not exist or
      cannot be parsed as CSV, raise FileNotFoundError or ValueError with a
      descriptive message immediately — do not produce a partial output file.
