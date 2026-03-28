skills:
  - name: classify_complaint
    description: RICE-aligned row classifier that applies role/intent/context/enforcement constraints to one complaint with traceable justification.
    input: "One CSV row as a dict containing complaint_id and description text (other fields may be present)."
    output: "Dict with keys: complaint_id, category, priority, reason, flag. category and priority use exact allowed values; flag is NEEDS_REVIEW or blank."
    error_handling: "If description is missing/empty or category is ambiguous, set category to Other, set flag to NEEDS_REVIEW, and provide a one-sentence reason citing available text (or missing-text condition)."

  - name: batch_classify
    description: RICE-aligned batch executor that reads input CSV, applies classify_complaint per row, and writes a complete output CSV.
    input: "Paths: input_path (test_[city].csv) and output_path (results_[city].csv)."
    output: "Output CSV with one row per input row and columns: complaint_id, category, priority, reason, flag."
    error_handling: "Must not crash on bad rows; continue processing remaining rows, emit a fallback row with category Other and flag NEEDS_REVIEW when a row is invalid, and still write the output file."

  

