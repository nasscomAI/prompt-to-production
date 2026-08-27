role: >
  A classifier agent that reads a single complaint row (dict) and outputs a
  classification dict. Its boundary is the classify_complaint function in
  classifier.py — it does not handle I/O, batching, or CSV parsing.

intent: >
  For every input complaint description, produce exactly one output row with
  category, priority, reason, and flag fields that match the schema. Every
  field is non-null; flag is "" unless genuinely ambiguous.

context: >
  The agent receives only the complaint row dict (complaint_id, description,
  etc.). It may NOT use external data sources, LLM calls, or human judgment.
  All classification decisions must be based on keyword/regex analysis of the
  description field alone.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other"
  - "Priority must be Urgent if description contains any of the severity keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse (including verb variants like collapsed/collapsing). Otherwise priority must be Standard."
  - "Every output row must include a reason field that cites specific words from the description"
  - "If category cannot be determined from description alone (ambiguous or no match), output category: Other and flag: NEEDS_REVIEW"
  - "Description: cited words must be verbatim excerpts from the input description field"
