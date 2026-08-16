# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag
    input: row — dict with keys: complaint_id, date_raised, city, ward, location, description, reported_by, days_open
    output: dict with keys: complaint_id, category, priority, reason, flag
      - category: exactly one of Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other
      - priority: Urgent or Standard (Urgent if severity keywords present in description)
      - reason: one sentence citing specific words from the description
      - flag: NEEDS_REVIEW or blank (blank when category is determinate)
    error_handling: If description is missing or empty, returns category: Other, priority: Standard, reason: "Insufficient description", flag: NEEDS_REVIEW
    error_handling_ambiguous: If category cannot be determined from description alone, outputs category: Other and flag: NEEDS_REVIEW

  - name: batch_classify
    description: Reads input CSV, applies classify_complaint per row, writes output CSV
    input: input_path — path to test_[city].csv; output_path — path to write results CSV
    output: writes results CSV with columns: complaint_id, category, priority, reason, flag
    error_handling: If input file not found, raises ValueError with clear message. Does not crash on bad rows — logs warning and produces output even if some rows fail.
    error_handling_ambiguous: Reports rows that required NEEDS_REVIEW flagging; ensures output CSV is always produced with all rows processed.
