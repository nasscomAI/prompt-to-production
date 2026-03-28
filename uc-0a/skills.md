# skills.md

skills:
  - name: classify_complaint
    description: Classify one complaint description into category, priority, reason, and review flag using the UC-0A fixed taxonomy.
    input: A dictionary with at minimum `description` (string); optional `complaint_id` for traceability.
    output: A dictionary with exact keys `category`, `priority`, `reason`, `flag`.
    error_handling: If description is empty or non-text, return `category: Other`, `priority: Standard`, `reason: Insufficient description to determine issue type.`, and `flag: NEEDS_REVIEW`.

  - name: batch_classify
    description: Read an input CSV of complaints, apply `classify_complaint` row-wise, and write a deterministic output CSV.
    input: `input_path` (CSV path) and `output_path` (CSV path), with each row containing a complaint description field.
    output: Output CSV preserving original rows plus appended/updated `category`, `priority`, `reason`, `flag` columns.
    error_handling: If file/column errors occur, fail fast with a clear error message; continue per-row on bad records using `Other` + `NEEDS_REVIEW` instead of silently dropping rows.
