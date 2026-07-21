skills:
  - name: classify_complaint
    description: Classifies a single complaint row into a category, priority, reason, and review flag using only the complaint description.
    input: A dict representing one CSV row, with at least a description field plus complaint_id, ward, and location.
    output: A dict with keys complaint_id, category, priority, reason, flag — category from the fixed 10-value list, priority from Urgent/Standard/Low, reason as one sentence citing words from the description, flag as NEEDS_REVIEW or blank.
    error_handling: >
      If the description is missing or empty, return category Other, priority Standard,
      reason noting no description was provided, and flag NEEDS_REVIEW. If no category
      keyword matches, return category Other and flag NEEDS_REVIEW rather than guessing.
      Severity keywords always force priority Urgent even when the category is Other.

  - name: batch_classify
    description: Reads the input CSV, applies classify_complaint to every row, and writes the results CSV.
    input: Path to the input test_[city].csv and a path for the output results CSV.
    output: A results CSV with columns complaint_id, category, priority, reason, flag — one row per input complaint, written even if some rows fail.
    error_handling: >
      Must not crash on a malformed or partial row: any row that raises is written with
      category Other, priority Standard, flag NEEDS_REVIEW, and a reason noting the row
      could not be classified. Reports the count of rows processed and rows flagged.
