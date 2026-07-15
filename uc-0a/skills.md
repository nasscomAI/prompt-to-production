skills:
  - name: classify_complaint
    description: Classify one complaint row into category, priority, reason, and flag.
    input: "CSV row object with description (required), category (optional/stripped), priority_flag (optional/stripped)."
    output: "Object: {category, priority, reason, flag}."
    error_handling: "If category is indeterminate, return {category: Other, flag: NEEDS_REVIEW} and still provide priority and reason from available description evidence."

  - name: batch_classify
    description: Read an input CSV, apply classify_complaint to each row, and write a compliant output CSV.
    input: "Input CSV file path containing complaint descriptions."
    output: "Output CSV with columns: description, category, priority, reason, flag."
    error_handling: "If required columns are missing, fail with a schema error; if more than 20% rows are ambiguous, complete output and emit a warning for manual review."
