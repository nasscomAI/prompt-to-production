# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag.
    input: A dictionary (row) with at least complaint_id and description keys, as read from a test_[city].csv file.
    output: A dictionary with exactly the keys complaint_id, category, priority, reason, flag — where category and priority are exact allowed strings, reason is exactly one sentence citing specific words from the description, and flag is blank or NEEDS_REVIEW.
    error_handling: Missing or empty description → category: Other and flag: NEEDS_REVIEW. Any of the nine severity keywords present → priority: Urgent regardless of category. A description matching a non-allowed label (Dead Animal, Sanitation, Animal Carcass, Noise Pollution, Electrical Hazard, Heritage Lighting, Cracked Road, etc.) → map to the nearest allowed category; if none fits → category: Other, flag: NEEDS_REVIEW. Genuinely ambiguous between two allowed categories (e.g. flooding vs drain blockage, heritage vs streetlight) → category: Other, flag: NEEDS_REVIEW; never invent a category or sub-category.

  - name: batch_classify
    description: Reads an input CSV, applies classify_complaint to every row, and writes a results CSV with one classified row per input row.
    input: input_path (path to a test_[city].csv) and output_path (path to a results_[city].csv).
    output: Writes a CSV at output_path with columns complaint_id, category, priority, reason, flag — same row order as the input.
    error_handling: Never crashes on a bad row; malformed rows are skipped or written with a NEEDS_REVIEW flag, and the run always produces an output file even if some rows fail (per classifier.py: "flag nulls, not crash on bad rows, produce output even if some rows fail")