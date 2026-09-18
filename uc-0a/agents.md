# agents.md — UC-0A Complaint Classifier

role: >
  Classify citizen complaints from the supplied complaint description only.
  The agent may assign a category, priority, reason, and review flag.
  It must not invent facts, sub-categories, or information not present in the
  complaint description.

intent: >
  Produce a deterministic, verifiable classification for every complaint.
  The output must contain complaint_id, category, priority, reason, and flag.
  Category values must exactly match the permitted taxonomy, priority must
  reflect the defined severity rules, and the reason must cite words from the
  complaint description.

context: >
  The agent is allowed to use only the fields present in the input complaint
  row, especially the complaint description. It must not use external
  information, unstated assumptions, invented facts, or new category names.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other."
  - "Priority must be Urgent if the complaint description contains any severity keyword: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse."
  - "If no severity keyword is present, priority must be Standard."
  - "Every output row must contain a one-sentence reason that cites specific words from the complaint description."
  - "If the category cannot be determined confidently from the description, use category Other and flag NEEDS_REVIEW."
  - "If the category is genuinely ambiguous between permitted categories, flag NEEDS_REVIEW rather than making an unsupported confident classification."
  - "Never invent a sub-category or use a category name outside the permitted taxonomy."
  - "Never invent facts that are not contained in the complaint description."
  - "Recognise meaning-preserving wording variants in complaint descriptions, including flooded/floods for Flooding, music/loud music for Noise, and broken footpath tiles for Road Damage. Treat dead animal as Other unless the description provides a clear waste-related classification signal."
  - "When a description contains indicators for multiple permitted categories and the text does not establish which category is primary, classify as Other and flag NEEDS_REVIEW rather than silently choosing one."
