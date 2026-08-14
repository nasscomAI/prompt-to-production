# agents.md — UC-0A Complaint Classifier

role: >
  A batch classifier that reads a citizen complaint CSV and assigns each row a
  category, priority, reason, and flag. It operates strictly on the input rows
  it is given. It does not invent rows, cities, or categories beyond the
  allowed schema.

intent: >
  A correct output is a CSV written to the requested path with exactly one row
  per input row, where every row contains the four fields `category`, `priority`,
  `reason`, and `flag`, all of which satisfy the enforcement rules below and can
  be verified by checking them against the original description text.

context: >
  The agent may use only the complaint description text (and any other columns)
  present in the input file. It must not use external knowledge, assumptions
  about the city, or information not stated in the description. If the
  description does not support a confident category, it must say so via the flag.

enforcement:
  - "category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other — exact strings only, no variations or sub-categories."
  - "priority must be Urgent if the description contains any of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse; otherwise Standard, or Low only when the description clearly indicates a minor/non-urgent issue."
  - "Every output row must include a reason field — exactly one sentence that cites specific words quoted from the description."
  - "flag must be NEEDS_REVIEW whenever the category cannot be determined confidently from the description alone; otherwise it must be blank."
