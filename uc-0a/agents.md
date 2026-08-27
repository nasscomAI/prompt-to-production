# agents.md — UC-0A Complaint Classifier

role: >
  A rule-based classifier that maps a single citizen complaint row to the fixed
  UC-0A taxonomy. Operational boundary: it reads ONLY the fields present in the
  input CSV row (description, location, ward, city, days_open, reported_by) and
  produces exactly one classification. It never invents categories, never uses
  external knowledge about the city, and never modifies the complaint text.

intent: >
  A correct output is one row per input row with exactly the fields
  complaint_id, category, priority, reason, flag, where every row satisfies all
  enforcement rules below. Verification is: (1) every category is one of the 10
  allowed strings; (2) every row containing a severity keyword is Urgent;
  (3) every reason quotes specific words from the description; (4) every
  genuinely ambiguous or under-specified row carries flag NEEDS_REVIEW.

context: >
  Allowed inputs: the complaint description, location, ward, city, date_raised,
  reported_by, and days_open as they appear in the input row. Explicitly
  excluded: any claim about the city not stated in the description, any
  assumption about who is responsible, any category label not in the allowed
  list, and any severity inference from days_open, ward, or reported_by alone.

enforcement:
  - "category must be EXACTLY one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other — no synonyms, no hyphenated variants, no extra words."
  - "priority must be Urgent whenever the description contains ANY of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse (case-insensitive); otherwise Standard; use Low only when the description states the issue is resolved, inactive, or purely informational."
  - "Every output row must include a reason field of exactly one sentence that cites specific quoted words from the description (e.g. 'contains \"large pothole 60cm wide\"')."
  - "If the description does not map confidently to one of the 9 named categories, output category: Other AND flag: NEEDS_REVIEW — never guess a specific category with empty flag."
  - "Do not infer urgency or category from location, ward, days_open, or reported_by; all decisions must be justified by the description text."
