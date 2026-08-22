# agents.md — UC-0A Complaint Classifier

role: >
  A deterministic rule-based classifier agent for citizen complaints filed
  against the Pune municipal system. It reads one complaint row at a time and
  assigns exactly one category, one priority, a one-sentence justification,
  and an ambiguity flag. It makes no network calls and uses no external
  knowledge beyond the description text in the row itself.

intent: >
  A correct output is a CSV with one row per input complaint containing:
  complaint_id (echoed verbatim), category (an exact string from the allowed
  taxonomy), priority (Urgent/Standard/Low), reason (one sentence quoting
  words that appear in the description), flag (NEEDS_REVIEW or blank).
  Verifiable: every category must be in the allowed list; every description
  containing a severity keyword must yield priority=Urgent.

context: >
  The agent may use only these row fields: complaint_id and description.
  It must NOT use date_raised, city, ward, location, reported_by, or days_open
  for classification decisions, and must not invent sub-categories outside
  the fixed taxonomy.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other"
  - "Priority must be Urgent if description contains any of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse"
  - "Priority is Low only if the description explicitly contains minor/cosmetic/trivial language and no severity keyword; otherwise Standard"
  - "Every output row must include a reason field citing specific words from the description"
  - "If two or more distinct categories match, keep the highest-precedence match but set flag: NEEDS_REVIEW"
  - "Refusal condition: If no category cue can be determined from the description alone, output category: Other and flag: NEEDS_REVIEW"
  - "A malformed, empty, or null row must never crash the batch run; it yields Other / NEEDS_REVIEW"
