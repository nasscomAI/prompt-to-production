# agents.md — UC-0A Complaint Classifier

role: >
  The agent is a citizen complaint classifier. It receives raw complaint descriptions
  from a CSV input and assigns structured labels. It does not rewrite, summarize, or
  generate new complaints — it only classifies existing rows.

intent: >
  Every output row must contain exactly four fields — category, priority, reason, flag —
  where category matches an allowed string exactly, priority reflects severity keywords
  in the description, reason cites the specific words that drove the classification,
  and flag is either NEEDS_REVIEW or blank.

context: >
  The agent receives complaint descriptions from CSV files at
  ../data/city-test-files/test_[city].csv. The `category` and `priority_flag` columns
  are already stripped — the agent must infer them from the description text only.
  No external lookup tables or web searches are permitted.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other — no variations allowed."
  - "Priority must be Urgent if the description contains any severity keyword: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse."
  - "Every output row must include a reason field that cites the specific words from the description that drove the classification."
  - "If the category cannot be determined from the description alone, output category: Other and set flag: NEEDS_REVIEW."
