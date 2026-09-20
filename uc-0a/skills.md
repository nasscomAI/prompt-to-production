skills:
  - name: classify_complaint
    description: "Classify one complaint row using the fixed category and priority taxonomy."
    input: "One CSV row as a mapping containing complaint_id and complaint description."
    output: "A mapping with complaint_id, category, priority, reason, and flag."
    error_handling: "For ambiguity, return Other with NEEDS_REVIEW; for missing or malformed fields, retain the row identity where possible and return a reviewable result instead of raising."

  - name: batch_classify
    description: "Read a complaint CSV, apply classify_complaint to every row, and write the result CSV."
    input: "Input CSV path and output CSV path."
    output: "A CSV containing one result row per input row with the required output fields."
    error_handling: "Validate the input path and headers, report invalid rows through the output flag or reason, and continue processing remaining rows without crashing."
