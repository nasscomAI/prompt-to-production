# skills.md — UC-0A Skills Definition

skills:
  - name: classify_complaint
    description: Receives a single citizen complaint dictionary, maps it to a strict category, evaluates priority based on severity keywords, generates a one-sentence reason citing description text, and sets a flag if ambiguous.
    input: Dictionary with keys `complaint_id`, `description`, `location`, `ward`, etc.
    output: Dictionary with keys `complaint_id`, `category`, `priority`, `reason`, `flag`.
    error_handling: If description is missing/null or cannot be categorized with confidence, outputs `category: Other`, `priority: Standard`, `reason: Insufficient information in complaint description`, `flag: NEEDS_REVIEW`.

  - name: batch_classify
    description: Reads an input CSV containing citizen complaints, applies `classify_complaint` to every row, and writes the output dataset to a designated CSV file path.
    input: `input_path` (string path to input CSV), `output_path` (string path to output CSV).
    output: Writes output CSV file containing headers `complaint_id,category,priority,reason,flag`. Returns count of total and flagged rows.
    error_handling: Handles missing files, null/malformed rows gracefully without crashing, logging errors and setting `NEEDS_REVIEW` on problematic rows.
