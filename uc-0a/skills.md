skills:
  - name: classify_complaint
    description: Classifies a single municipal complaint row into a standardized category, priority level, single-sentence cited reason, and review flag.
    input: dict representing a complaint row with fields such as complaint_id, description, location, ward, city, reported_by, and days_open.
    output: dict containing complaint_id (str), category (str), priority (str), reason (str), and flag (str).
    error_handling: When input rows are empty, missing descriptions, or genuinely ambiguous, assigns category 'Other', flag 'NEEDS_REVIEW', and generates an explanatory single-sentence reason citing the issue or available text without raising unhandled exceptions.

  - name: batch_classify
    description: Reads an input CSV of citizen complaints, processes each complaint using classify_complaint with fault-tolerant error boundaries, and writes the structured classification results to a target CSV file.
    input: input_path (str path to source CSV file), output_path (str path to destination CSV file).
    output: Writes a CSV file containing columns complaint_id, category, priority, reason, flag.
    error_handling: Handles missing files, unreadable rows, and empty datasets gracefully by logging errors, yielding review-flagged fallback records for corrupted rows, and ensuring the output CSV is generated without process crashes.
