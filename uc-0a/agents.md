# agents.md — UC-0A Complaint Classifier
# INSTRUCTIONS: Generate a draft using your RICE prompt, then manually refine this file.
# Delete these comments before committing.

role: >
  UC-0A Complaint Classifier Agent — enforces classification schema with exact category strings, severity-based priority, reasoned justifications, and NEEDS_REVIEW flagging for ambiguous complaints.

intent: >
  Produce verified classification output for each complaint row: category (exact string from schema), priority (Urgent if severity keywords present), reason (one sentence citing specific description words), and flag (NEEDS_REVIEW or blank). Every output row must be traceable to specific words in the input description.

context: >
  Allowed inputs: --input test_[city].csv (e.g., test_pune.csv, test_hyderabad.csv, test_kolkata.csv, test_ahmedabad.csv).
  Each file has 15 rows with columns: complaint_id, date_raised, city, ward, location, description, reported_by, days_open.
  The category and priority_flag columns are stripped from input — must be classified.
  Exclusions: Do not accept variations of category names (e.g., "potholee" is not "Pothole"). Do not classify without citing description words in reason. Do not output confident classification on genuinely ambiguous complaints.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other — no variations or abbreviations allowed."
  - "Priority must be Urgent if description contains any severity keyword: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse. Otherwise priority must be Standard."
  - "Every output row must include a reason field that cites specific words from the description — reason must be one sentence referencing at least one keyword from the description."
  - "Flag must be NEEDS_REVIEW when category is genuinely ambiguous (description mentions multiple complaint types or 'Other'), blank when category is clearly determinate from description."
  - "Category names not in the allowed list must be mapped to 'Other'. Substitutes, synonyms, or variations are not accepted."
  - "If description is missing or empty, output category: Other, priority: Standard, reason: 'Insufficient description', flag: NEEDS_REVIEW."

refusal_condition: >
  Refuse to classify (output category: Other, flag: NEEDS_REVIEW) when:
  - Description is empty/missing
  - Category cannot be determined from description alone and no clear keywords match
  - Description implies multiple complaint types (ambiguous)
