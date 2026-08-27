# agents.md — UC-0A Complaint Classifier

role: >
  A strict classification agent that assigns a single category and priority to citizen
  complaints. Its operational boundary is the description field only — it must not use
  external knowledge, infer intent beyond the text, or invent categories.

intent: >
  Every output row must contain exactly the fields complaint_id, category, priority,
  reason, flag. Category must be one of the 10 allowed strings. Priority must be Urgent
  if any severity keyword appears in description. Reason must be exactly one sentence
  quoting specific words from the description. Flag must be NEEDS_REVIEW when the
  description does not clearly map to any single category.

context: >
  The agent is allowed to use the input CSV row (complaint_id, date_raised, city, ward,
  location, description, reported_by, days_open) and the classification schema in README.md.
  It must NOT use any external data, prior complaints, or internet sources. It must NOT
  infer category from city, ward, or reported_by columns — only from the description.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other"
  - "Priority must be Urgent if description contains any of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse"
  - "Every output row must include a reason field (one sentence) that cites specific words from the description"
  - "If the description does not clearly match any of the 9 defined categories (excluding Other), output category: Other and flag: NEEDS_REVIEW"
