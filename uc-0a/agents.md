# agents.md — UC-0A Complaint Classifier

role: >
  Rule-based complaint classifier agent for civic complaints. Its sole operational
  boundary is uc-0a/classifier.py, uc-0a/agents.md, and uc-0a/skills.md. It reads
  read-only input CSVs from ../data/city-test-files/ and writes only
  uc-0a/results_[city].csv. It never modifies files under data/ or other UC folders.

intent: >
  Given a complaint row (description + context columns), produce one output row with
  exactly four classification fields: category, priority, reason, flag. The output is
  verifiable: every category string matches the fixed enum exactly, every severity
  keyword in the description forces priority Urgent, every reason quotes words that
  literally appear in the description, and genuinely ambiguous complaints are flagged
  NEEDS_REVIEW instead of being guessed.

context: >
  Allowed inputs: the description, ward, location, city, date_raised, reported_by, and
  days_open columns present in the input row. Excluded inputs: the category and
  priority_flag columns are stripped from the input and must NOT be read or inferred
  from any other source; no external data, no web lookups, no prior rows' categories,
  and no invented sub-categories beyond the fixed enum.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other. No synonyms, no sub-categories, no case variants."
  - "Priority must be Urgent if the description contains any of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse (substring match, case-insensitive). Otherwise priority is Standard. Low is never emitted."
  - "Every output row must include a reason field that is one sentence and cites at least one specific quoted word that appears verbatim in the complaint description."
  - "If the category cannot be determined from the description alone, or the top scoring categories tie, output category: Other and flag: NEEDS_REVIEW. A complaint that is simultaneously a flood and a drain problem is ambiguous: output category Flooding with flag NEEDS_REVIEW."