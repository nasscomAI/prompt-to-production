# agents.md — UC-0A Complaint Classifier

role: >
  Complaint Classifier agent for civic grievance triage. Takes one row from a
  city complaint CSV (complaint_id, date_raised, city, ward, location,
  description, reported_by, days_open) and returns a classification for that
  row only. Does not aggregate across rows, does not compare complaints to
  each other, and does not use any information beyond the row's own fields.
  Runs fully offline via classifier.py — no network calls, no external model.

intent: >
  A correct run produces results_[city].csv with one output row per input row,
  same order, exactly the columns complaint_id, category, priority, reason,
  flag. "Correct" is checked against three things: (1) category is always one
  of the 10 allowed values, never a synonym or invented sub-category; (2) every
  description containing a severity keyword is Urgent, with zero exceptions;
  (3) reason names the exact word(s) from the description that drove the
  decision, so a human can verify the call without re-reading the whole row.

context: >
  Allowed input: the description field of the current row (category signal),
  plus the row's own complaint_id (passthrough only). Excluded: ward, location,
  reported_by, days_open, date_raised — none of these may influence category
  or priority. Excluded: any other row in the file, any external knowledge
  about the city, any category not in the fixed enum below.

enforcement:
  - "category must be exactly one of: Pothole, Flooding, Streetlight, Waste,
     Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other —
     never a variant spelling, never a new sub-category."
  - "priority must be Urgent whenever the description contains any of: injury,
     injured, injuries, child, children, school, hospital, hospitalised,
     hospitalized, ambulance, fire, hazard, hazardous, fell, fall, collapse,
     collapsed — this check runs independently of category and overrides any
     other priority signal."
  - "priority defaults to Standard when no severity keyword is present. Low is
     used only when the description itself describes the issue as minor or
     purely cosmetic — never inferred from ward or days_open."
  - "reason is exactly one sentence and must quote the specific word or phrase
     from the description that drove the category, and (when Urgent) the
     severity keyword that drove the priority."
  - "flag is NEEDS_REVIEW when the description matches zero categories, or
     matches two or more categories with no way to prefer one from the text
     alone. flag is blank in every other case — no other flag value exists."
  - "Refusal condition: never guess a specific category under ambiguity to
     avoid an empty-looking output. An ambiguous row must be category: Other,
     flag: NEEDS_REVIEW, with a reason naming which categories tied."
