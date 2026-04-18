skills:
  - name: classify_complaint
    description: Classify one civic complaint row into the UC-0A schema using only the complaint text and row-local fields.
    input: A single complaint row as a dict, JSON object, or CSV row including the complaint text and any available identifiers.
    output: A valid JSON object with exactly four top-level keys: category, priority, reason, and flag.
    error_handling: If the complaint is ambiguous or unsupported by the text alone, return category as Other and flag as NEEDS_REVIEW; never invent missing facts.

  - name: batch_classify
    description: Read the input CSV, apply classify_complaint to each row, and write the classified results to the output file.
    input: An input CSV path and an output CSV path, or equivalent file-path arguments.
    output: A results CSV containing one classified row per complaint, with the schema fields derived from the JSON classification.
    error_handling: Skip or flag malformed rows instead of crashing, preserve output for the remaining rows, and mark ambiguous cases with NEEDS_REVIEW.
