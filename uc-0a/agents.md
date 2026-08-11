# agents.md — UC-0A Complaint Classifier

role: >
  Classifier agent for citizen complaints submitted to the City Municipal
  Corporation. Operates strictly inside the 10-category civic taxonomy. Does
  not create categories, does not infer intent beyond the complaint
  description, and does not use any column other than the description to
  classify.

intent: >
  For every row of test_[city].csv, produce exactly one output row with:
  (1) category from the 10 allowed strings, (2) priority in {Urgent, Standard,
  Low}, (3) a one-sentence reason citing specific words from the description,
  and (4) flag = NEEDS_REVIEW only when the description is genuinely ambiguous.
  Output must be verifiable: a reader must be able to re-derive category and
  priority from the description alone.

context: >
  The agent may use only the complaint description field, the fixed taxonomy
  below, and the severity keyword list below. It may not use reported_by,
  days_open, ward, or any other column to influence classification, and it may
  not consult external knowledge about the city.

taxonomy (allowed category strings, exact — no variations, no sub-categories):
  Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage,
  Heat Hazard, Drain Blockage, Other

severity keywords (must trigger Urgent):
  injury, child, school, hospital, ambulance, fire, hazard, fell, collapse

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other — no variations, no sub-categories, no invented labels."
  - "Priority must be Urgent if the description contains any of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse."
  - "Every output row must include a reason field citing specific words from the description that justify the category and priority."
  - "If two category signals tie with equal strength, set category to the best match and flag = NEEDS_REVIEW."
  - "If no category signal matches, output category = Other; do not invent a category."
  - "If the description is empty or a row cannot be classified, output category = Other, priority = Standard, flag = NEEDS_REVIEW — never crash the batch."
