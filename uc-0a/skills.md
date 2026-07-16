# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into a category, priority, reason, and review flag.
    input: One complaint row (at minimum a `description` string field) from the input CSV.
    output: >
      An object with category (one of: Pothole, Flooding, Streetlight, Waste,
      Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other),
      priority (Urgent, Standard, or Low), reason (one sentence citing specific
      words from the description), and flag (NEEDS_REVIEW or blank).
    error_handling: >
      If the description does not clearly support one category, output
      category: Other and flag: NEEDS_REVIEW rather than guessing. If any
      severity keyword (injury, child, school, hospital, ambulance, fire,
      hazard, fell, collapse) is present, priority is always Urgent regardless
      of category ambiguity.

  - name: batch_classify
    description: Reads the input CSV, applies classify_complaint to every row, and writes the results CSV.
    input: Path to an input CSV (e.g. ../data/city-test-files/test_[city].csv) with category and priority_flag columns stripped.
    output: Path to an output CSV (e.g. results_[city].csv) with the original columns plus category, priority, reason, and flag for every row.
    error_handling: >
      If a row is missing a description or the input file is malformed, skip
      writing category/priority for that row and instead set flag:
      NEEDS_REVIEW with a reason explaining the missing/invalid input, rather
      than failing the whole batch.
