# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag per the README schema.
    input: >
      A dict for one complaint row with at least: complaint_id, description.
      Other columns (date_raised, city, ward, location, reported_by, days_open)
      may be present and are used only as supporting context.
    output: >
      A dict with keys complaint_id, category, priority, reason, flag.
      category ∈ {Pothole, Flooding, Streetlight, Waste, Noise, Road Damage,
      Heritage Damage, Heat Hazard, Drain Blockage, Other};
      priority ∈ {Urgent, Standard, Low}; reason is one sentence citing words
      from the description; flag is "NEEDS_REVIEW" or "".
    error_handling: >
      If description is missing/empty, return category "Other", priority
      "Standard", flag "NEEDS_REVIEW", and a reason noting the missing
      description. If the category is genuinely ambiguous, set category "Other"
      and flag "NEEDS_REVIEW". Severity keywords always force priority "Urgent".
      Never raise on a single row.

  - name: batch_classify
    description: Reads the input CSV, applies classify_complaint to every row, and writes the results CSV.
    input: >
      input_path (str) — path to test_[city].csv with header:
      complaint_id, date_raised, city, ward, location, description, reported_by,
      days_open. output_path (str) — destination for the results CSV.
    output: >
      Writes a CSV to output_path with header complaint_id, category, priority,
      reason, flag and one row per input complaint. Returns nothing meaningful.
    error_handling: >
      Must not crash on a malformed or partial row: catch per-row failures,
      emit a row with category "Other", priority "Standard", flag "NEEDS_REVIEW",
      and a reason describing the failure, then continue. Flag null/empty fields.
      Always produce an output file even if some rows fail.
