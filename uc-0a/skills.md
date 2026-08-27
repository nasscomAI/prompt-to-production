# skills.md

skills:
  - name: classify_complaint
    description: Classifies one citizen complaint row into category, priority, reason, and flag.
    input: A single complaint row as a dict — complaint_id, date_raised, city, ward, location, description, reported_by, days_open.
    output: A dict with keys complaint_id, category, priority, reason, flag. category is one of the ten exact strings; priority is Urgent | Standard | Low; flag is NEEDS_REVIEW or blank.
    error_handling: If category cannot be determined from description alone, output category: Other and flag: NEEDS_REVIEW. priority must be Urgent if description contains any of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to every row, and writes the results CSV.
    input: A CSV path (test_[city].csv) with headers complaint_id, date_raised, city, ward, location, description, reported_by, days_open.
    output: A CSV written to the given output path with columns complaint_id, category, priority, reason, flag.
    error_handling: Never crashes on a bad row — flag it for review and continue. Produces output even if some rows fail. Blank flag written as empty string.
