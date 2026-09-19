skills:
  - name: classify_complaint
    description: Classifies one complaint row into category, priority, reason and flag.
    input: One dict (a CSV row) with at least complaint_id and description.
    output: Dict with complaint_id, category, priority, reason, flag.
    error_handling: Empty or missing description returns category Other, flag NEEDS_REVIEW. No keyword match returns Other with NEEDS_REVIEW. Multiple category matches set NEEDS_REVIEW.

  - name: batch_classify
    description: Reads the input CSV, applies classify_complaint to every row and writes the results CSV.
    input: input_path (str) and output_path (str) for CSV files.
    output: CSV file with columns complaint_id, category, priority, reason, flag.
    error_handling: A row that fails is written as Other with NEEDS_REVIEW instead of crashing. Output is always written.