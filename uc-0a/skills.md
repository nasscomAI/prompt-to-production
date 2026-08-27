# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint description into category, priority, reason, and flag.
    input: A single complaint description string.
    output: JSON object with keys category (string), priority (string), reason (string), flag (string or empty).
    error_handling: If the description is empty or unintelligible, outputs category: Other, priority: Standard, reason: "Description too ambiguous to classify", flag: NEEDS_REVIEW.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes the enriched CSV to an output path.
    input: Path to input CSV (must contain a description column), path for output CSV.
    output: Output CSV with original columns plus category, priority, reason, flag appended.
    error_handling: If the input CSV is missing or lacks a description column, raises a clear error. Rows with empty descriptions are classified as Other/NEEDS_REVIEW; valid rows are processed individually.
