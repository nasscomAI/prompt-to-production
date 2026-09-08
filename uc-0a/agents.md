# agents.md — UC-0A Complaint Classifier

role: >
  A deterministic complaint classifier that assigns each citizen complaint to a fixed
  taxonomy of categories and priorities. Operates on a single CSV row at a time using
  keyword-based rules — no LLM calls, no external services.

intent: >
  Every input row must produce exactly four fields: category (exact string from the
  allowed list), priority (Urgent or Standard or Low), reason (one sentence citing
  specific words from the description), and flag (NEEDS_REVIEW or blank). Output must
  be reproducible — same input always yields same output.

context: >
  The agent reads only the complaint_id and description fields from each input row.
  It does not access date, city, ward, location, or reported_by for classification
  decisions. External knowledge or assumptions about local context are not allowed.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other"
  - "Priority must be Urgent if description (case-insensitive) contains any of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse"
  - "Every output row must include a reason field that cites at least one specific word or phrase from the input description"
  - "If no keyword matches any category, output category: Other and flag: NEEDS_REVIEW"
  - "If description is null or empty, output category: Other, priority: Low, flag: NEEDS_REVIEW"
