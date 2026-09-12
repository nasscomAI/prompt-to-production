# skills.md

skills:
  - name: classify_complaint
    description: Classify one complaint row into category, priority, reason, and flag.
    input: A single complaint row as a dict (complaint_id, location/ward, and free-text description).
    output: A dict with keys complaint_id, category, priority, reason, flag.
    error_handling: When the description alone does not map to a listed category, set category to
      Other and flag to NEEDS_REVIEW; never guess or invent details not present in the text.

  - name: batch_classify
    description: Apply classify_complaint to every row of an input CSV and write the results.
    input: Path to an input CSV (test_[city].csv) and a path for the output CSV.
    output: A CSV with columns complaint_id, category, priority, reason, flag — one row per input.
    error_handling: Null or malformed rows are flagged rather than crashing; the job keeps going
      and still writes a complete output file even if individual rows fail.
