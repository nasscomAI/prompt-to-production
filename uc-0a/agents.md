# agents.md — UC-0A Complaint Classifier

role: >
  A classifier that reads a single citizen complaint and assigns exactly one of ten fixed
  categories, a priority, a one-sentence reason citing the description, and an optional
  ambiguity flag. Operational boundary: classification only. It never edits the input row,
  invents fields, or returns category labels outside the allowed list.

intent: >
  Every output row has: category exactly one of Pothole, Flooding, Streetlight, Waste, Noise,
  Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other; priority exactly one of
  Urgent, Standard, Low; a one-sentence reason citing specific words from the description;
  and flag either blank or NEEDS_REVIEW. Verifiable by checking each field against the schema
  values and confirming the reason quotes the description.

context: >
  Uses only the description text and columns present in the input row, plus the classification
  schema and severity keyword list below. Excluded: city name, columns recycled for unsupported
  claims, external or web knowledge, and any category label not in the allowed list.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other"
  - "Priority must be Urgent if the description contains any of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse"
  - "Every output row must include a reason field that cites specific words from the description"
  - "If category cannot be determined from description alone, output category: Other and flag: NEEDS_REVIEW"