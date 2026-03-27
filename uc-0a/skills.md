# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

**Core failure modes:** Taxonomy drift · Severity blindness · Missing justification · Hallucinated sub-categories · False confidence on ambiguity

skills:
  - name: classify_complaint
    description: Classify a single citizen complaint row into exactly one of the 10 allowed categories, assign priority based on severity keywords, produce a cited reason, and flag ambiguity with NEEDS_REVIEW.
    input: dict with keys complaint_id (str) and description (str). The description is the only data source — category and priority_flag columns are stripped.
    output: dict with keys complaint_id (str), category (one of 10 allowed values), priority (Urgent | Standard | Low), reason (one sentence citing specific words from description), flag (NEEDS_REVIEW or empty string)
    error_handling: If description is empty or missing, return category: Other, priority: Low, reason: cites missing description, flag: NEEDS_REVIEW. If description is ambiguous across multiple categories, return best match with flag: NEEDS_REVIEW and reason explaining the ambiguity. Never raise an exception on a single row.

  - name: batch_classify
    description: Read an input CSV from ../data/city-test-files/test_[city].csv, apply classify_complaint to each row, write results to uc-0a/results_[city].csv.
    input: input_path (str, path to CSV with complaint_id and description columns; category and priority_flag columns are stripped), output_path (str, path to write results CSV)
    output: CSV file at output_path with columns: complaint_id, category, priority, reason, flag
    error_handling: Skip malformed rows and continue processing. Log warnings for rows that fail. Ensure output CSV is written even if some rows produce errors. Catch CSV read/write errors and report them without crashing. One bad row must not prevent the remaining 14 rows from being classified.
