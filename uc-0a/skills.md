# skills.md

skills:
  - name: classify_complaint
    description: Classifies one complaint row into category, priority, reason, and flag.
    input: A single complaint row as a dict with keys: complaint_id, date_raised, city, ward, location, description, reported_by, days_open.
    output: A dict with keys: complaint_id, category, priority, reason, flag. Category is exactly one of Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other. Priority is Urgent if description contains injury, child, school, hospital, ambulance, fire, hazard, fell, or collapse; otherwise Standard or Low. Reason is exactly one sentence citing specific words from the description. Flag is NEEDS_REVIEW only when the category is genuinely ambiguous, otherwise blank.
    error_handling: If the category cannot be determined from the description alone, output category: Other and flag: NEEDS_REVIEW. Never infer facts absent from the description, never invent sub-categories, and never rewrite the allowed category list.

  - name: batch_classify
    description: Reads an input CSV of complaint rows, applies classify_complaint to each row, and writes a results CSV.
    input: An input path to a test_[city].csv file with columns complaint_id, date_raised, city, ward, location, description, reported_by, days_open (category and priority_flag columns are stripped).
    output: Writes a CSV to the output path with one row per input row: complaint_id, category, priority, reason, flag.
    error_handling: Must not crash on bad rows — flag nulls and continue; always produce output even if some rows fail. Never modify the input file.
