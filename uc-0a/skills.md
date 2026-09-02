skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag
    input: dict with keys: complaint_id, description
    output: dict with keys: complaint_id, category, priority, reason, flag
    error_handling: Returns category: Other, priority: Standard, flag: NEEDS_REVIEW when category cannot be determined

  - name: batch_classify
    description: Reads input CSV, applies classify_complaint per row, writes output CSV
    input: input_path (str), output_path (str)
    output: writes results CSV with columns: complaint_id, category, priority, reason, flag
    error_handling: flags nulls, does not crash on bad rows, produces output even if some rows fail