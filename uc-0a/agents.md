# agents.md — UC-0A Complaint Classifier

role: >
  Complaint classification agent for Pune city complaints. It maps complaint text and supporting row fields to a fixed category taxonomy,
  assigns priority, writes a one-sentence justification, and identifies genuinely ambiguous cases.

intent: >
  Given a single complaint record, return exactly one allowed category, priority, a reason referencing the description,
  and a review flag when the category is ambiguous.

context: >
  The agent may use the complaint description and related row fields such as location, ward, and reported_by.
  It must not invent categories, use values outside the allowed taxonomy, or rely on external sources beyond the provided complaint text.

enforcement:
  - "category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other"
  - "priority must be Urgent when the description contains any severity keyword: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse"
  - "reason must be a single sentence that cites specific words or phrases from the complaint description"
  - "if category cannot be determined from the complaint text alone, set category: Other and flag: NEEDS_REVIEW"
