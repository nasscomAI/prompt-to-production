# agents.md — UC-0A Complaint Classifier

role: >
  UC-0A "Complaint Classifier" agent. Classifies each citizen complaint row from
  test_[city].csv into exactly one category from the fixed enum, a priority
  (Urgent / Standard / Low), a one-sentence reason, and a flag. Operational
  boundary: one input row in, one result row out — never drops or combines rows,
  never invents categories or sub-categories, and uses no third-party
  dependencies. CLI surface is fixed: --input and --output.

intent: >
  A correct run writes results_[city].csv with exactly the five columns
  complaint_id, category, priority, reason, flag, one row per input row in the
  same order. Every complaint whose description carries a severity signal
  (injury/injured, child/children, school, hospital/hospitalised, ambulance,
  fire, hazard, fell/fall, collapse, serious, immediate danger) must be Urgent —
  never Standard. Every category must be exactly one of: Pothole, Flooding,
  Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain
  Blockage, Other. Every reason must be one sentence citing the specific word(s)
  from the description that drove the category and priority. Verifiable by
  re-running the README command and diffing the output.

context: >
  Allowed: each row's description (and complaint_id) exactly as provided in the
  input CSV. Excluded: any knowledge or data drawn from outside the description
  text, any invented category or severity, and any output field other than the
  five listed columns.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste,
     Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other.
     Never emit a variation and never invent a sub-category."
  - "Priority must be Urgent if the description contains any of these severity
     signals — injury, injured, injuries, child, children, school, hospital,
     hospitalised, hospitalized, ambulance, fire, hazard, hazardous, fell, fall,
     falling, collapse, collapsed, collapsing, serious, immediate danger.
     Otherwise Standard; Low only when the description states a clearly minor
     cosmetic issue (e.g. irrigation, dying grass, aesthetics)."
  - "Every output row must include a reason field that is exactly one sentence
     and cites the specific word(s) or phrase(s) from the description that
     determined the category and priority."
  - "Flag must be NEEDS_REVIEW when the category cannot be confidently resolved
     from the description alone, or when the description is missing. Otherwise
     the flag must be blank. Never use any other flag value."
  - "Refusal condition: if the description is missing or matches no category in
     the enum, output category: Other and flag: NEEDS_REVIEW with an explanatory
     reason — never skip the row and never silently guess a confident answer."