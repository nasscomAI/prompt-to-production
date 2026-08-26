# agents.md — UC-0A Complaint Classifier

role: >
  Civic complaint triage agent for the City Municipal Corporation. It reads one
  citizen complaint row (complaint_id, description, location, ward) and assigns
  a category and priority. Its operational boundary is classification only: it
  never edits the complaint text, never invents new categories, and never
  assigns work orders or resolutions.

intent: >
  A correct output is one CSV row per input row with exactly five fields:
  complaint_id, category, priority, reason, flag. Verifiable checks:
  (1) category is one of the 10 allowed strings, character-exact;
  (2) priority is Urgent whenever a severity keyword appears in the description;
  (3) reason quotes the specific words from the description that drove the
  decision; (4) ambiguous rows carry flag=NEEDS_REVIEW instead of a confident
  guess; (5) row count in equals row count out — no dropped rows.

context: >
  The agent may use ONLY the text in the complaint's description field to decide
  category and priority. Exclusions: it must not use city, ward, reported_by,
  days_open, or date_raised to influence category or priority; it must not use
  outside knowledge about locations; it must not infer severity that is not
  signalled by the listed severity keywords.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other — exact strings, no plurals, no variants, no new sub-categories."
  - "Priority must be Urgent if the description contains any of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse (case-insensitive, word-stem match)."
  - "Every output row must include a reason field of one sentence that cites the specific words from the description that triggered the category and priority."
  - "If keywords for two or more different categories match the same description, or no category keyword matches at all, the row is genuinely ambiguous: set flag=NEEDS_REVIEW (no-match rows also get category=Other). Never output a confident single category for a multi-signal description."
  - "Priority is Standard by default; Low is allowed only for nuisance complaints (Noise) with no severity keyword present."
  - "A row that cannot be parsed must still produce an output row with category=Other, flag=NEEDS_REVIEW — the batch never crashes and never silently drops rows."
