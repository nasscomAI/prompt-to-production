# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag.
    input: One complaint row with description text and any available metadata.
    output: YAML object containing category, priority, reason, and flag.
    error_handling: If description is ambiguous or category cannot be determined, set category to Other, flag to NEEDS_REVIEW, and explain the ambiguity in reason.

  - name: batch_classify
    description: Reads an input CSV file, applies classify_complaint to each row, and writes an output CSV.
    input: Path to a complaint input CSV file.
    output: CSV file with classified rows containing category, priority, reason, and flag.
    error_handling: Validate input columns, skip malformed rows with a warning, and preserve any row-level classification errors in the output.
