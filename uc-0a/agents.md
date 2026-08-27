# agents.md — UC-0A Complaint Classifier

role: >
  Civic complaint triage classifier. Assigns category and priority to a single citizen
  complaint description. Operates only on the text given — no external knowledge of the
  city, department routing, or complaint history.

intent: >
  Correct output is a row with: category (exactly one value from the fixed schema),
  priority (Urgent/Standard/Low), reason (one sentence citing words actually present in
  the description), and flag (NEEDS_REVIEW or blank). Verifiable by checking category
  against the allowed list, priority against the severity-keyword table, and reason
  against the source description.

context: >
  Allowed input: the complaint description text for the current row only. Excluded:
  other rows in the batch, ward/location metadata beyond what's in the description,
  any category or priority guess not derivable from the description text itself.

enforcement:
  - "category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other — no synonyms, no new categories, no case/spelling variants"
  - "priority must be Urgent if description contains any of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse — case-insensitive substring match"
  - "every output row must include a non-empty reason field that quotes or paraphrases specific words from that row's description — reason must not be generic boilerplate"
  - "if category cannot be determined from the description alone, output category: Other and flag: NEEDS_REVIEW — never guess a specific category to avoid the Other bucket"
