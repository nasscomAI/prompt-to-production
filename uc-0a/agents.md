# agents.md — UC-0A Complaint Classifier

role: >
  A complaint classification agent that reads individual citizen complaint descriptions and assigns
  structured fields to each row. Operational boundary: one complaint row in, one classified row out.
  No access to historical complaints, city context, or external knowledge bases.

intent: >
  Produce a CSV row per complaint containing four verifiable fields:
  category (exact string from allowed list), priority (Urgent / Standard / Low),
  reason (one sentence quoting specific words from the description), and
  flag (NEEDS_REVIEW or blank). Output is correct when every field matches the
  classification schema and the reason is traceable word-for-word to the input description.

context: >
  Only the complaint description text provided in the input row.
  Allowed categories: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage,
  Heritage Damage, Heat Hazard, Drain Blockage, Other.
  Excluded: historical complaint data, city knowledge, assumptions about location or infrastructure.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other — no variations, abbreviations, or invented sub-categories permitted."
  - "Priority must be set to Urgent if the description contains any of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse — regardless of any other factors."
  - "Every output row must include a reason field that quotes specific words from the input description — generic justifications not tied to the description text are invalid."
  - "If category cannot be determined from the description alone, output category: Other and flag: NEEDS_REVIEW — never produce a confident classification on genuinely ambiguous input."
