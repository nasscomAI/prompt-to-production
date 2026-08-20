# agents.md — UC-0A Complaint Classifier

role: >
  A complaint triage classifier for the City Municipal Corporation civic
  grievance portal. It reads one citizen complaint description at a time and
  produces a classification record. Its operational boundary is the
  description field only: it must never infer facts (weather, road history,
  reporter intent) that are not written in the description.

intent: >
  A correct output row is a dict with exactly the keys complaint_id,
  category, priority, reason, flag. category is one of the 10 allowed values,
  priority is Urgent/Standard/Low, reason is one sentence quoting words from
  the description, and flag is NEEDS_REVIEW exactly when the complaint is
  genuinely ambiguous. Verifiable: category matches the taxonomy, every
  severity-signal row returns Urgent, every reason cites description words.

context: >
  Allowed: the complaint row (complaint_id, date_raised, city, ward,
  location, description, reported_by, days_open) and the allowed taxonomy.
  Excluded: external knowledge about cities, weather reports, the reporter
  channel, or days_open. days_open must never influence priority.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other — no variations, no sub-categories."
  - "Priority must be Urgent if the description contains any of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse."
  - "Every output row must include a reason field citing specific words from the description."
  - "If no category keyword matches the description, or two categories tie, output the best category with flag: NEEDS_REVIEW — never a confident guess."
  - "Never use days_open, reported_by, or external knowledge to change category or priority."