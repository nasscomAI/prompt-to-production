# skills.md

skills:
  - name: classify_complaint
    description: Classifies one complaint row into the four UC-0A fields: category, priority, reason, and flag.
    input: One complaint row (dict) with at least complaint_id, location, description, and days_open.
    output: A dict with keys complaint_id, category, priority, reason, flag — category from the 10-value list, priority from (Urgent, Standard, Low), and a one-sentence reason quoting words from the description.
    error_handling: If the category cannot be determined from the description alone, returns category: Other and flag: NEEDS_REVIEW instead of guessing; never drops the row.

  - name: batch_classify
    description: Reads an input CSV, applies classify_complaint to every row, and writes the results CSV.
    input: Path to test_[city].csv (rows with complaint_id, location, description, days_open; category and priority_flag columns stripped) and an output path.
    output: A CSV with one row per input row and columns complaint_id, category, priority, reason, flag — same row count as the input, rows never dropped.
    error_handling: Flags nulls and produces output even if some rows fail; reports per-row failures without crashing the batch.
