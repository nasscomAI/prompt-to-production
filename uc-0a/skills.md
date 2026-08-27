# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single complaint row based on RICE constraints and exact category lists.
    input: A single complaint row dictionary (e.g. description text).
    output: A dictionary containing category, priority, reason, and flag.
    error_handling: Return category 'Other', flag 'NEEDS_REVIEW' and an explanatory reason if input is invalid or ambiguous.

  - name: batch_classify
    description: Reads complaints from an input CSV, classifies each row individually, and writes to an output CSV.
    input: Two string parameters representing the input CSV path and the output CSV path.
    output: None (writes an output CSV file with identical structure plus classification columns).
    error_handling: Must flag nulls or invalid data, continue processing without crashing on bad rows, and ensure the output CSV is generated even if some rows fail.
