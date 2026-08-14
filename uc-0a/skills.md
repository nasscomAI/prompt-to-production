# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag using only the words in that row's description.
    input: One complaint row (dict) containing complaint_id, description, location, ward, reported_by, and days_open.
    output: A dict with complaint_id and exactly four fields — category (one of Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other), priority (Urgent, Standard, or Low), reason (one sentence quoting the sentence of the description that contains the deciding keyword), and flag (NEEDS_REVIEW or blank).
    error_handling: Priority is Urgent whenever the description contains any of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse. Low is used only when the issue is clearly minor (a trigger like minor, cosmetic, mild, slight) and no severity keyword applies. If the category cannot be determined from the description alone, or the description genuinely supports more than one category (including when a near-miss runner-up is within one keyword), the row returns category: Other with flag: NEEDS_REVIEW instead of guessing.

  - name: batch_classify
    description: Reads an input complaints CSV, applies classify_complaint to every row, and writes a results CSV with one classification row per input row.
    input: Input CSV path (test_[city].csv with a header row) and output CSV path.
    output: A CSV written to the output path with columns complaint_id, category, priority, reason, flag — one row per input row, never altering the input file.
    error_handling: Skips or flags null/malformed rows instead of crashing; still produces output even if some rows fail, so a single bad row never aborts the batch.
