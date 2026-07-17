# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into a category, priority, one-sentence justified reason, and an ambiguity flag, per the enforcement rules in agents.md.
    input: >
      A dict for one CSV row with fields complaint_id, date_raised, city, ward,
      location, description, reported_by, days_open (category and priority_flag
      are not present — they are being generated).
    output: >
      A dict with keys: complaint_id, category (exactly one of Pothole, Flooding,
      Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain
      Blockage, Other), priority (Urgent, Standard, or Low), reason (one sentence
      citing specific words from description), flag (NEEDS_REVIEW or blank).
    error_handling: >
      If description is missing or blank, return category "Other", priority "Low",
      reason "No description provided", flag "NEEDS_REVIEW" — never raise on a
      single row.

  - name: batch_classify
    description: Reads the input CSV, applies classify_complaint to every row, and writes the results CSV — producing output even when individual rows fail.
    input: >
      input_path (str) — path to test_[city].csv.
      output_path (str) — path to write results_[city].csv.
    output: >
      A CSV file at output_path with header complaint_id,category,priority,reason,flag
      and one row per input row, in the same order as the input.
    error_handling: >
      If classify_complaint raises for a row, catch the exception, log a warning
      with the complaint_id, and write a fallback row (category "Other", priority
      "Low", reason describing the failure, flag "NEEDS_REVIEW") instead of
      aborting the run. The output file must always be written.
