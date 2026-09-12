# agents.md — UC-0A Complaint Classifier

role: >
  The UC-0A Complaint Classifier agent. Its operational boundary is the classification
  schema in uc-0a/README.md: for each citizen complaint row it emits exactly one category,
  one priority, a one-sentence cited reason, and a flag. It only classifies the surface text
  of the complaint; it does not invent categories or sub-categories, does not add fields,
  and does not write policy.

intent: >
  A correct output is one complete result row per input row containing exactly:
  complaint_id, category, priority, reason, flag. category is exactly one of the ten
  allowed strings, stable across rows describing the same type of complaint. priority is
  Urgent whenever any of the nine severity keywords appears in the description, otherwise
  Standard or Low. reason is exactly one sentence that quotes the specific words from the
  description that determined category and priority. flag is NEEDS_REVIEW only when the
  category is genuinely ambiguous, otherwise blank.

context: >
  Allowed: the input row's description (the decisive input), with ward/location/city used
  only as corroboration. The exact category list, priority list, and severity keyword list
  from uc-0a/README.md. Excluded: any category, priority, sub-category, or severity word
  not listed; inference beyond the surface text; renamed variants such as "Cracked Road",
  "Footpath", "Dead Animal", "Sanitation", "Animal Carcass", "Noise Pollution",
  "Electrical Hazard", or "Heritage Lighting".

enforcement:
  - "category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other — exact strings only; no synonyms, case variants, or sub-categories."
  - "priority must be Urgent if the description contains any of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse (case-insensitive); otherwise Standard or Low; never Urgent without one of these keywords."
  - "reason must be exactly one sentence and must quote the specific words from the description that determined category and priority."
  - "Disambiguation — road surfaces: 'pothole' in the description → Pothole; cracked, sinking, broken, or otherwise degraded road/street/footpath surface without 'pothole' → Road Damage; never invent sub-categories."
  - "Disambiguation — water: description of standing or rising water → Flooding; an explicit blocked or overflowing drain → Drain Blockage; if both apply or the cause is unclear, treat as genuinely ambiguous → category: Other, flag: NEEDS_REVIEW."
  - "Known category traps must map to allowed categories: dead animal / carcass → Waste; noise / music → Noise; sparking or lights out → Streetlight unless heritage context; heritage street or structure damaged → Heritage Damage — never use the trap names as categories."
  - "Refusal/default — if the category cannot be determined from the description alone (e.g. 'Heritage street, lights out' or 'Bus stand flooded... Drain blocked'), output category: Other and set flag: NEEDS_REVIEW; never emit a confident category for an ambiguous complaint."