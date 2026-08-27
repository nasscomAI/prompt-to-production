role: >
  Complaint classification agent operating on citizen grievance descriptions.
  Its boundary is a single CSV row — it never accesses external data, never
  invokes an LLM, and never modifies the input. It outputs only a structured
  dict with the keys: complaint_id, category, priority, reason, flag.

intent: >
  Given a row containing a complaint_id and description, produce exactly one
  output row where category is one of the 10 allowed strings, priority is
  Urgent/Standard/Low based on severity keywords found in the description,
  reason is a sentence that quotes at least 3 words from the description, and
  flag is either blank or NEEDS_REVIEW. Every input row must yield an output
  row — the tool may not skip or silently drop rows.

context: >
  Allowed: complaint_id, description, location (only for disambiguation of
  heritage-related terms). Excluded: date_raised, city, ward, reported_by,
  days_open — these must never influence category or priority.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other. No abbreviations, no casing variations."
  - "Priority must be Urgent if description contains ANY of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse. Otherwise Standard. Low is reserved for future use and should NOT be assigned."
  - "Every output row must include a reason field that is one sentence citing at least 3 consecutive words from the description."
  - "If category cannot be determined from description alone (no keyword match), output category: Other and flag: NEEDS_REVIEW. If category IS determined, flag must be blank."
