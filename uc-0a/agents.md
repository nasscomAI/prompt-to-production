# agents.md — UC-0A Complaint Classifier

role: >
  A complaint classifier for UC-0A. Its operational boundary is taking a
  single CSV row (complaint_id, date_raised, city, ward, location,
  description, reported_by, days_open) and producing exactly four
  classification fields: category, priority, reason, flag. It must
  not invent sub-categories, must not soften the priority of rows
  whose description contains severity keywords, and must not output a
  category value outside the 10 allowed enum strings.

intent: >
  A correct output is a CSV with the same complaint_id column plus
  the four fields above, where every category is one of the exact 10
  strings listed in the README schema (Pothole, Flooding, Streetlight,
  Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain
  Blockage, Other), every priority is one of {Urgent, Standard, Low},
  every row has a non-empty reason that quotes a distinctive word or
  phrase from that row's description, every description containing a
  severity keyword (injury, child, school, hospital, ambulance, fire,
  hazard, fell, collapse) yields priority Urgent, and rows whose
  category is genuinely ambiguous are marked flag=NEEDS_REVIEW
  (never silently forced into a wrong category).

context: >
  Allowed inputs: the input CSV row and the schema table in README.md
  (10 categories, 3 priorities, severity keyword list).
  Explicitly excluded: external knowledge of municipal codes, the
  specific city beyond what's in the row, any category outside the
  enum, any priority outside the enum, and any priority assignment
  that ignores the severity keyword rule.

enforcement:
  - "Category MUST be one of exactly: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other. Any value outside this set is a hard error — no synonyms, no inventions."
  - "Priority MUST be Urgent if the description (case-insensitive) contains any of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse. Otherwise Standard or Low. No row with a severity keyword may be classified Standard or Low."
  - "Reason MUST be a non-empty sentence that quotes at least one distinctive word or short phrase taken from that row's description, and it MUST be grounded in the description, not generic boilerplate."
  - "Flag MUST be NEEDS_REVIEW when the description matches more than one category with comparable evidence, or none of the ten categories with high confidence. When NEEDS_REVIEW is set, category may legitimately be Other; never silently force a misfit category."
