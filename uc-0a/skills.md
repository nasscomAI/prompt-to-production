# skills.md — UC-0A Complaint Classifier
# Refined from the RICE draft. Defines the two skills the agent executes.

skills:
  - name: classify_complaint
    description: >
      Classify one complaint row into an exact category, a priority, a one-sentence
      reason that cites actual words from the description, and an optional review flag.
    input: >
      A single row as a dict from the CSV (complaint_id, date_raised, city, ward,
      location, description, reported_by, days_open).
    output: >
      A dict with keys: complaint_id, category, priority, reason, flag.
      category is exactly one of: Pothole, Flooding, Streetlight, Waste, Noise,
      Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other.
      priority is exactly one of: Urgent, Standard, Low.
      flag is "NEEDS_REVIEW" (ambiguity / no match) or "".
    error_handling: >
      If no category keyword matches, category becomes "Other" and flag becomes
      NEEDS_REVIEW. If the top two categories score equally, the higher-priority
      category wins and flag becomes NEEDS_REVIEW. Raises no exceptions for bad
      text inputs; an empty description yields category "Other", NEEDS_REVIEW.

  - name: batch_classify
    description: >
      Read an input CSV, apply classify_complaint to every row, and write a results
      CSV (complaint_id, category, priority, reason, flag).
    input: >
      input_path: path to test_[city].csv; output_path: path to results_[city].csv.
    output: >
      Writes a CSV with header complaint_id, category, priority, reason, flag and
      one row per successfully classified input row. Prints a count of rows written.
    error_handling: >
      A malformed row never crashes the batch: the row is logged with its line
      number and skipped, remaining rows are still processed, and the output file
      is still produced. Missing columns default to empty strings.