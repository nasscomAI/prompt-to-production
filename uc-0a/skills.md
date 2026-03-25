skills:
  - name: classify_complaint
    description: Classifies one complaint row to strict category and priority with traceable reason.
    input: One CSV row dictionary containing complaint_id and description.
    output: Dictionary with complaint_id, category, priority, reason, and flag.
    error_handling: If description is empty or signals are ambiguous, return category Other with flag NEEDS_REVIEW.

  - name: batch_classify
    description: Reads input CSV, applies complaint classification row-wise, and writes result CSV.
    input: Input CSV path and output CSV path.
    output: Output CSV with columns complaint_id, category, priority, reason, flag.
    error_handling: Never crash on bad rows and continue processing by writing NEEDS_REVIEW fallback row.
