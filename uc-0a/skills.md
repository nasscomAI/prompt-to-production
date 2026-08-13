# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into one allowed category, one priority, a one-sentence reason, and an optional flag.
    input: One dict row from the input CSV — at minimum the complaint description, possibly with other columns such as city, complaint_id, and timestamp.
    output: A dict with exactly the keys complaint_id, category, priority, reason, flag.
    error_handling: If the category cannot be determined from the description alone, outputs category: Other, flag: NEEDS_REVIEW, and a reason explaining the uncertainty. Never guesses or invents categories.

  - name: batch_classify
    description: Reads the input CSV, applies classify_complaint to every row, and writes the results CSV.
    input: Paths to the input CSV (test_[city].csv, category and priority_flag columns stripped) and the output CSV (results_[city].csv).
    output: A CSV with columns complaint_id, category, priority, reason, flag — one row per input row.
    error_handling: Never crashes on a bad row; null and malformed rows are marked NEEDS_REVIEW or skipped with the failure recorded, and a results file is still produced for all rows that could be processed.
