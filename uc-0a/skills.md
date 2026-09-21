skills:
  - name: classify_complaint
    description: Classifies one complaint row using the fixed UC-0A taxonomy and urgency rules.
    input: "A dictionary containing complaint_id and a text description, optionally with CSV metadata."
    output: "A dictionary containing complaint_id, category, priority, reason, and flag."
    error_handling: "Missing or blank descriptions produce category Other, priority Standard, a reason citing the missing description, and NEEDS_REVIEW; ambiguous descriptions are flagged rather than guessed."

  - name: batch_classify
    description: Reads a complaint CSV, applies classify_complaint to every row, and writes a result CSV.
    input: "Input CSV path with a complaint_id column and a description column."
    output: "CSV with one result row per input row and columns complaint_id, category, priority, reason, and flag."
    error_handling: "Reports file and row errors, continues processing valid rows, and writes a result for malformed or missing descriptions instead of silently dropping rows."
