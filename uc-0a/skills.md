skills:
  - name: classify_complaint
    description: Takes one complaint row and returns its category, priority, one-sentence reason and review flag, following the enforcement rules in agents.md.
    input: >
      One complaint as a dict, taken from a CSV row with columns complaint_id, date_raised,
      city, ward, location, description, reported_by, days_open. Only description and
      complaint_id are used for classification. All values are strings.
    output: >
      A dict with exactly these keys:
      complaint_id (string, copied from input),
      category (string, exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other),
      priority (string, exactly one of: Urgent, Standard, Low),
      reason (string, one sentence quoting specific words from the description),
      flag (string, either NEEDS_REVIEW or an empty string).
    error_handling: >
      If description is missing, empty, whitespace-only or unrelated to any complaint type,
      return category: Other, priority: Standard, flag: NEEDS_REVIEW and a reason saying the
      description could not be classified. If complaint_id is missing, return an empty
      complaint_id and flag: NEEDS_REVIEW. If the description matches a severity keyword
      (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse; case-insensitive,
      stem match), priority must be Urgent even when the category is uncertain. If the description
      fits two or more categories equally well, set flag: NEEDS_REVIEW instead of guessing
      confidently. Never return a category or priority outside the allowed values, and never raise
      an exception to the caller.

  - name: batch_classify
    description: Reads an input CSV, applies classify_complaint to every row, and writes a results CSV with one output row per input row.
    input: >
      Two file paths. input_path is a CSV with the columns complaint_id, date_raised, city,
      ward, location, description, reported_by, days_open (15 rows per city, category and
      priority_flag columns already stripped). output_path is where the results CSV is written.
    output: >
      A CSV file at output_path with the header complaint_id, category, priority, reason, flag
      and one row per input row, in the same order as the input. Rows that fail classification
      are still written.
    error_handling: >
      If the input file is missing or has no description column, stop with a clear error message
      and write no partial file. If an individual row is malformed, has null fields or raises an
      error inside classify_complaint, do not crash: write that row with category: Other,
      flag: NEEDS_REVIEW and a reason naming the problem, then continue. Always write the output
      file even when some rows fail. Report the count of rows read, rows written and rows flagged
      NEEDS_REVIEW when finished, and never silently drop a row.
