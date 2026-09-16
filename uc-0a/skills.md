skills:
  - name: classify_complaint
    description: Classifies one complaint row into the approved category and priority schema with a cited reason and review flag.
    input: "Dictionary containing at least complaint_id and description string fields from the input CSV."
    output: "Dictionary with complaint_id, category, priority, reason, and flag."
    error_handling: "Raises a clear error for missing required fields or blank descriptions; ambiguous descriptions return category Other with flag NEEDS_REVIEW."
  - name: batch_classify
    description: Reads a complaint CSV, applies classify_complaint to every row, and writes the required result CSV.
    input: "UTF-8 CSV path with complaint_id and description columns, plus output CSV path."
    output: "UTF-8 CSV with columns complaint_id, category, priority, reason, flag and one row per input row."
    error_handling: "Raises clear errors for missing files, missing columns, null records, invalid paths, or write failures; never silently skips bad data."
