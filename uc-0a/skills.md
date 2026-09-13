# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classify one complaint record into category, priority, reason, and flag following uc-0a/agents.md.
    input: One complaint record (dict) containing complaint_id, description, and other source fields (date_raised, city, ward, location).
    output: A dict with exactly these keys in order — complaint_id, category, priority, reason, flag.
    category_rule: Category must be exactly one of the fixed enum — Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other. Never invent or vary a category.
    priority_rule: Priority must be Urgent if the description contains any severity indicator (injury/injured, child/children, school, hospital/hospitalised, ambulance, fire, hazard, fell/fall, collapse/collapsed, serious, immediate danger). Otherwise Standard; Low only for minor cosmetic issues.
    reason_rule: Reason must be exactly one sentence that cites one or more specific words or phrases from the description and states why the category was chosen.
    flag_rule: Flag must be NEEDS_REVIEW when the complaint is genuinely ambiguous or the category cannot be confidently determined; otherwise blank (empty). Never use any other flag value.
    ambiguity_rule: If category cannot be confidently resolved from the description alone, set category to Other and flag to NEEDS_REVIEW; still provide a reason.
    error_handling: Never invent a category, never skip the complaint, and never emit a field missing or malformed.

  - name: batch_classify
    description: Read an input CSV of complaint records, classify every row via classify_complaint, and write the results CSV.
    input: A CSV file path with columns complaint_id, date_raised, city, ward, location, description, reported_by, days_open.
    process_rule: Apply classify_complaint to every input row; do not skip or drop any row.
    preserve_rule: Preserve every complaint_id unchanged from input to output.
    output_rule: Write a valid CSV with exactly these columns in this order — complaint_id, category, priority, reason, flag.
    output_path_rule: Write the results to the path supplied by the --output argument; overwrite it if it exists.
    rigor_rule: If a row cannot be classified confidently, emit it with category Other and flag NEEDS_REVIEW rather than omitting it.
    error_handling: Do not crash unnecessarily; if a malformed row is found, still emit an output row for it with flag NEEDS_REVIEW rather than dropping it.
