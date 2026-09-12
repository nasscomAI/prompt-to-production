# skills.md

skills:
  - name: classify_complaint
    description: Classifies one complaint row into category + priority + reason + flag per the fixed taxonomy.
    input: One complaint row as a dict (uses complaint_id and description).
    output: Dict with keys complaint_id, category, priority, reason, flag.
    error_handling: Never raises on bad rows — returns category Other with flag NEEDS_REVIEW when the description is missing or genuinely ambiguous.

  - name: batch_classify
    description: Reads an input city CSV, applies classify_complaint to every row, writes the results CSV.
    input: Input CSV path and output CSV path (strings).
    output: Results CSV with columns complaint_id, category, priority, reason, flag — one row per input.
    error_handling: Flags nulls, isolates per-row failures so one bad row never aborts the run, and always writes output even if some rows fail.
