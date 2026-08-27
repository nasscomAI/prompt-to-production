role: >
  Complaint classification agent. Operates on individual complaint rows from a CSV.
  Classifies each row into category, priority, reason, and flag.
  Does not use external APIs, LLMs, or internet access. Uses only keyword rules defined in this file.

intent: >
  For every input row, produce exactly one output row with:
    complaint_id — preserved from input
    category    — exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other
    priority    — Urgent if severity keywords present, else Standard or Low
    reason      — one sentence citing specific words from the description
    flag        — NEEDS_REVIEW when category is ambiguous or cannot be determined, else blank

context: >
  Uses only the complaint description field. The description is the sole signal for classification.
  Excludes reported_by, days_open, and ward from influencing decisions.
  Excludes any external knowledge — classification must be determinable from description text alone.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other"
  - "Priority must be Urgent if description contains any of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse"
  - "Priority must be Low if category is Noise and no Urgent keywords are present"
  - "Every output row must include a reason field citing specific words from the description"
  - "If category cannot be determined from description alone, output category: Other and flag: NEEDS_REVIEW"
