# skills.md

skills:
  - name: classify_complaint
    description: Map a single complaint description into a structured classification output (category, priority, reason, flag).
    input: A dictionary/object containing keys `description`, optionally other row fields (e.g., `id`, `location`).
    output: A dictionary/object with keys `category`, `priority`, `reason`, `flag`.
    error_handling: If input is missing or empty, return `category: Other`, `priority: Low`, `reason: 'Empty or invalid description'`, `flag: NEEDS_REVIEW`.

  - name: batch_classify
    description: Read an input CSV, apply `classify_complaint` for each row, and write an output CSV with the complete output schema.
    input: Path to input CSV file with complaint rows and path to output CSV file destination.
    output: Written CSV file where each row has `category`, `priority`, `reason`, `flag` plus original row identifiers.
    error_handling: Log/collect row-level errors; for malformed rows use `Other`/`Low`/`NEEDS_REVIEW` and continue processing the rest.
