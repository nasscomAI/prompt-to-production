skills:
  - name: classify_complaint
    description: Classify one complaint row into a fixed civic issue category, priority, reason, and review flag.
    input: A dict-like CSV row with complaint_id, description, and other metadata fields.
    output: A dict with complaint_id, category, priority, reason, and flag.
    error_handling: Returns Other, Low, and NEEDS_REVIEW when the description is missing, ambiguous, or does not match the taxonomy.

  - name: batch_classify
    description: Read an input complaints CSV, classify each row, and write a results CSV.
    input: Input CSV path and output CSV path.
    output: A CSV file with complaint_id, category, priority, reason, and flag columns.
    error_handling: Continues past bad rows, writes fallback rows for unexpected exceptions, and always produces an output file when the input is readable.
