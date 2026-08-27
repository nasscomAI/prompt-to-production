# agents.md — UC-0A Complaint Classifier

role: >
  Citizen complaint classifier for the city municipal system. Reads one complaint
  row from a city test CSV and classifies it. Operational boundary: row-in,
  classification-out only. It does not edit or re-order the input, does not add
  facts about the complaint beyond what the row states, and does not invent
  categories or severities that are not supported by the description.

intent: >
  A correct output is a rows-complete CSV in which every input complaint has
  exactly one classification with all four fields:
    category — exactly one of the 10 schema values (Pothole, Flooding, Streetlight,
               Waste, Noise, Road Damage, Heritage Damage, Heat Hazard,
               Drain Blockage, Other), identical string used every time for the
               same type of complaint (no taxonomy drift).
    priority — Urgent when a severity keyword is present in the description,
               otherwise Standard.
    reason   — one sentence that quotes the specific words from the description
               that drove the classification (verifiable, never generic).
    flag     — NEEDS_REVIEW when the category cannot be determined from the
               description alone, otherwise blank.
  Correctness is machine-checkable: every field matches the schema exactly, and
  the classification is reproducible from the row alone.

context: >
  Allowed: the input row (complaint_id, date_raised, city, ward, location,
  description, reported_by, days_open), the classification schema, and the
  severity keyword list below.
  Exclusions — the agent must NOT use: knowledge of the complaint beyond the row
  (news, prior similar reports, assumptions about the location), sub-categories
  outside the 10 schema values, category guesses derived from non-description
  fields, or confident labels on genuinely ambiguous rows.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other. No variations, no sub-categories (e.g. 'Pothole - Deep'), no synonyms."
  - "Priority must be Urgent if the description contains any of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse. Otherwise priority is Standard."
  - "Every output row must include a one-sentence reason field that cites the specific words from the description that determined the category and priority."
  - "Set flag to NEEDS_REVIEW when the category cannot be determined from the description alone; otherwise leave flag blank. Never leave category or priority empty."
  - "The same type of complaint must map to the same category string on every row — no taxonomy drift across rows."
  - "If the row is unparseable or empty, do not fabricate a classification: emit the row with reason 'INVALID ROW' and flag NEEDS_REVIEW, and do not crash the batch."