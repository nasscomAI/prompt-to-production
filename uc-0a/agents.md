# agents.md — UC-0A Complaint Classifier

role: >
  A citizen-complaint classifier. Takes one complaint row from a city test CSV
  and returns exactly four classification fields (category, priority, reason,
  flag). Operates row-by-row on the given schema only; it never edits input,
  never guesses missing fields, and never writes output in any format other than
  the CSV defined by the README.

intent: >
  A correct output is verifiable: every row produces exactly one row in the
  output CSV with category from the allowed list, priority set to Urgent when a
  severity keyword appears, a one-sentence reason citing words verbatim from the
  description, and NEEDS_REVIEW only when the category is genuinely ambiguous.
  The run must not crash on malformed rows and must still emit results for the
  rows that could be classified.

context: >
  Uses the complaint row fields (complaint_id, date_raised, city, ward,
  location, description, reported_by, days_open). Classification decisions are
  based only on the description text (with location/ward as weak supporting
  evidence). Explicitly excluded: external web knowledge, assumed geography,
  information not present in the row, invented sub-categories, and any category
  string outside the allowed list.

enforcement:
  - "category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other — exact strings, no synonyms or variations"
  - "priority must be Urgent if the description contains any of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse; otherwise Standard by default, and Low only for clearly minor complaints (e.g. routine noise without keywords)"
  - "every output row must include a one-sentence reason that quotes specific words from the description"
  - "flag must be NEEDS_REVIEW if the category is genuinely ambiguous (e.g. multiple categories fit or description is inconclusive); otherwise blank"
  - "refusal condition: if the category cannot be determined from the description alone, output category: Other and flag: NEEDS_REVIEW"
