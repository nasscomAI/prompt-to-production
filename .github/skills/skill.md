# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into a category, priority, reason, and ambiguity flag using rule-based keyword enforcement.
    input: A dict representing one CSV row with keys — complaint_id, description (and optional: date_raised, city, ward, location, reported_by, days_open).
    output: A dict with exactly four keys — category (one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other), priority (Urgent / Standard / Low), reason (one sentence citing specific words from the description), flag (NEEDS_REVIEW or blank).
    error_handling: If description is null or empty, returns category=Other, priority=Low, flag=NEEDS_REVIEW, and a reason stating no description was provided. If category cannot be determined from the description alone, defaults to Other and sets flag=NEEDS_REVIEW. Priority is always forced to Urgent when description contains any of the severity keywords — injury, child, school, hospital, ambulance, fire, hazard, fell, collapse — regardless of category match.

  - name: batch_classify
    description: Reads an input CSV of complaint rows, applies classify_complaint to each row, and writes a results CSV with classification outputs.
    input: Two strings — input_path (path to test_[city].csv with columns complaint_id, date_raised, city, ward, location, description, reported_by, days_open) and output_path (path to write results CSV).
    output: A CSV file at output_path with columns — complaint_id, category, priority, reason, flag — one row per input complaint. File is written even if some rows fail.
    error_handling: Wraps each row classification in a try/except; on error writes category=Other, priority=Low, flag=NEEDS_REVIEW, and a reason describing the exception. Never crashes the full batch due to a single bad row.