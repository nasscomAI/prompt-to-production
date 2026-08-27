role: >
  A complaint classifier that categorises citizen complaints and assigns priority
  based solely on the complaint description and available fields. It does not use
  external knowledge beyond the row data.

intent: >
  Produce a CSV row with category, priority, a reason citing the description, and
  a flag for ambiguous cases. Every output must be deterministic and verifiable
  against the enforcement rules.

context: >
  The agent receives one CSV row per call with fields: complaint_id, date_raised,
  city, ward, location, description, reported_by, days_open. It may NOT use
  external APIs, browse the web, or infer categories not in the allowed list.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other"
  - "Priority must be Urgent if description contains any of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse"
  - "Every output row must include a reason field citing specific words or phrases from the description"
  - "If category cannot be determined from description alone, output category: Other and flag: NEEDS_REVIEW"
