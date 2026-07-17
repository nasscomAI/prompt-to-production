skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into category, priority, reason, and flag according to the UC-0A schema.
    input: >
      One complaint record (dict or CSV row) containing at minimum a
      description field, plus any other input columns (e.g. city, complaint id).
      The category and priority_flag columns are absent and must not be assumed.
    output: >
      A dict/row with four fields: category (exact string, one of Pothole,
      Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage,
      Heat Hazard, Drain Blockage, Other), priority (Urgent, Standard, or Low),
      reason (one sentence citing specific words from the description),
      flag (NEEDS_REVIEW or blank).
    error_handling: >
      If the description does not clearly support any single category, set
      category to Other and flag to NEEDS_REVIEW rather than guessing. If a
      severity keyword (injury, child, school, hospital, ambulance, fire,
      hazard, fell, collapse) is present, priority must be forced to Urgent
      even if other cues suggest otherwise. If the description is empty or
      missing, set category to Other, priority to Low, flag to NEEDS_REVIEW,
      and reason to state that no description was provided — never invent a
      category or reason from nothing.

  - name: batch_classify
    description: Reads the input CSV for a city, applies classify_complaint to every row, and writes the results CSV in the required output format.
    input: >
      Path to an input CSV (../data/city-test-files/test_[city].csv) with
      15 complaint rows per city; category and priority_flag columns are
      stripped from this file.
    output: >
      Path to an output CSV (uc-0a/results_[city].csv) containing every
      original input column plus the four classify_complaint output fields
      (category, priority, reason, flag), with exactly one output row per
      input row and no rows skipped or reordered.
    error_handling: >
      If the input file is missing or unreadable, fail with a clear error
      naming the expected path rather than producing a partial output file.
      If a row is malformed or missing required fields, still emit one output
      row for it with category Other, priority Low, flag NEEDS_REVIEW, and a
      reason noting the row was malformed — the row count of output must
      always match the row count of input. If any classify_complaint result
      uses a category string outside the allowed list, batch_classify must
      reject it and substitute Other with flag NEEDS_REVIEW rather than write
      an invalid value to the CSV.
