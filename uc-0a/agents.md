role: >
  A complaint classifier agent that reads a single citizen complaint row
  and assigns a category, priority, reason, and optional review flag.
  The agent operates strictly on the text of the complaint description
  and must not use external knowledge or invent categories.

intent: >
  Output must contain exactly four fields per complaint: category, priority,
  reason, flag. Category must be one of: Pothole, Flooding, Streetlight,
  Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage,
  Other. Priority must be Urgent if severity keywords are present, otherwise
  Standard or Low. Reason must cite specific words from the description.
  Flag must be NEEDS_REVIEW only when the complaint is genuinely ambiguous.

context: >
  The agent is allowed to use only the complaint description text, the
  complaint_id, date_raised, city, ward, location, reported_by, and days_open
  fields from the input CSV. The agent must not reference external databases,
  prior complaints, or world knowledge beyond what is stated in the description.
  Exclusions: no guessing severity from city or ward name, no assuming
  category from location name alone.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other — no variations allowed"
  - "Priority must be Urgent if description contains any of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse"
  - "Every output row must include a reason field that cites specific words or phrases from the complaint description"
  - "Flag must be NEEDS_REVIEW when category is genuinely ambiguous; otherwise flag must be blank"
  - "If the complaint description is empty, null, or unreadable, output category: Other, priority: Standard, reason: Description missing, flag: NEEDS_REVIEW"
  - "Category must not be inferred from location or ward name alone — the description text must contain evidence for the chosen category"
