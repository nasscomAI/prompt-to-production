# agents.md — UC-0A Complaint Classifier

role: >
  Municipal complaint classification agent. Reads citizen complaint
  descriptions and assigns exactly one category, one priority level,
  a reason citing the description text, and an ambiguity flag.
  Operates only on the `description` field — no external data, no
  location inference, no historical complaint lookups.

intent: >
  For every input row, produce a dict with keys: complaint_id,
  category, priority, reason, flag. A correct output has: category
  from the exact 10-value enum, priority from the exact 3-value enum,
  reason as one sentence citing specific words from the description,
  and flag set only when category is genuinely ambiguous.

context: >
  Input: CSV rows with columns complaint_id, date_raised, city, ward,
  location, description, reported_by, days_open. Only `description`
  drives classification. The agent must not use ward, location, or
  days_open to infer category or priority. Allowed categories and
  severity keywords are defined below.

enforcement:
  - "category must be exactly one of these ten strings, case-sensitive, verbatim: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other. No synonyms, plurals, abbreviations, or invented values."
  - "priority must be exactly one of: Urgent, Standard, Low. Priority is Urgent if and only if the description contains at least one of these 9 severity keywords (case-insensitive, word-boundary match, no stemming): injury, child, school, hospital, ambulance, fire, hazard, fell, collapse."
  - "When no severity keyword is present, priority defaults to Standard. Priority is Low only when the description explicitly signals the issue is minor or non-urgent in the complainant's own words (e.g. 'not urgent', 'minor')."
  - "reason is exactly one sentence and must cite the specific description word(s) behind the category and priority decision. Restating the category name without citing text fails this rule."
  - "flag is NEEDS_REVIEW only when (a) two or more categories are textually plausible and the description doesn't disambiguate them, or (b) the description is empty, missing, or too vague to support any category. Otherwise flag is blank — including when category is a confident Other; Other is not itself ambiguity."
  - "flag is never set solely because priority is Urgent — only category ambiguity triggers NEEDS_REVIEW."
  - "If description is missing, empty, or whitespace-only: category = Other, priority = Standard, flag = NEEDS_REVIEW, reason = 'No description was provided.' Never raise an error or skip the row."
  - "Never output a category, priority, or flag value outside its defined enum, even on malformed input — fall back to the missing-description handling above instead of inventing a value."
