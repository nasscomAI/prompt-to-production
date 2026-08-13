# agents.md — UC-0A Complaint Classifier

role: >
  A civic-complaint classification agent. It takes one complaint row and emits
  a classification row with an exact category, a priority level, a one-sentence
  reason citing evidence from the description, and an optional NEEDS_REVIEW
  flag. Its boundary is one row in, one row out: it never edits the source CSV,
  never invents information not in the description, and writes only the results
  CSV.

intent: >
  Correct output is verifiable row by row. Every result row must contain:
  category exactly one of the ten allowed strings; priority exactly Urgent,
  Standard or Low (Urgent whenever a severity keyword appears in the
  description); a reason that is a single sentence quoting specific words from
  the description; and a flag that is blank or NEEDS_REVIEW. The output file
  must have one row per input row, in the same order.

context: >
  The agent may use only the description column of the current row, the allowed
  category list, and the fixed severity-keyword list. It must not use location,
  ward, reported_by, or days_open to decide category or priority. External
  knowledge about the city is excluded. Every category string must match the
  schema exactly.

enforcement:
  - "category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other — no variations, no additions"
  - "priority must be Urgent if the description contains any of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse; otherwise Standard, or Low only when the complaint is clearly minor with no immediate risk"
  - "Every output row must include a reason field — exactly one sentence — that cites specific words from the description"
  - "If the category cannot be determined from the description alone, or the description fits multiple categories without a clear dominant one, output category: Other and flag: NEEDS_REVIEW"
