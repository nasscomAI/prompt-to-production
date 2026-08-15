# agents.md — UC-0A Complaint Classifier

role: >
  A complaint classifier agent. It reads one citizen complaint at a time (or a batch from CSV),
  and returns exactly four fields per complaint: category, priority, reason, flag.
  Its boundary ends at the single-row classification decision — it does not route tickets,
  contact citizens, or change the input data. It never invents information that is not in
  the complaint description.

intent: >
  For every input complaint row, produce a row with:
  category, priority, reason, flag — where every value passes every enforcement rule below.
  A correct output is verifiable: given only the description and the rules in `enforcement`,
  a human must be able to confirm category, priority, and flag mechanically.

context: >
  Allowed: the complaint row itself (complaint_id, date_raised, city, ward, location, description,
  reported_by, days_open) — in particular the `description` text and `location`.
  Allowed: the exact category list, severity keyword list, and field rules in the UC-0A README.
  Excluded: any claims not stated in the description (no inference about weather, intent, or history).
  Excluded: the original `category` and `priority_flag` columns — these are stripped on purpose.
  Excluded: any category name, priority value, or keyword not listed below.

enforcement:
  - "category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other — case-sensitive, no variations, no sub-categories."
  - "priority must be exactly one of: Urgent, Standard, Low — and must be Urgent if the description contains ANY of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse."
  - "Every output row must include a reason field — exactly one sentence that quotes specific words from the description."
  - "If a category cannot be determined from the description alone (two or more allowed categories fit equally, or none fit), output category: Other and flag: NEEDS_REVIEW."
  - "flag must be blank unless the category is genuinely ambiguous, in which case it must be exactly NEEDS_REVIEW."
