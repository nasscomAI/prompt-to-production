skills:
  - name: classify_complaint
    description: Classifies one complaint row into the fixed UC-0A schema.
    input: One CSV row as a dict with complaint_id, description, city, ward, location, reported_by, and days_open fields.
    output: A dict with complaint_id, category, priority, reason, and flag.
    error_handling: Returns Other, Standard, a review reason, and NEEDS_REVIEW when the row is missing a usable description or the category is ambiguous.

  - name: batch_classify
    description: Reads an input CSV, applies classify_complaint to each row, and writes the results CSV.
    input: Input CSV path and output CSV path as strings.
    output: A CSV file containing the classified complaint rows.
    error_handling: Skips row-level crashes, preserves the complaint_id when present, and writes an error-safe fallback row for malformed input.
