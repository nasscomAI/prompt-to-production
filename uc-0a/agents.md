# agents.md — UC-0A Complaint Classifier

role: >
  Municipal complaint classifier for UC-0A: map each citizen complaint row to exactly one allowed
  category, one priority level, a one-sentence justification, and an optional review flag. Operates
  only on fields present in the input CSV (especially `description`); does not invent locations,
  dates, or facts not supported by the text. Does not call external APIs or use live maps.

intent: >
  For every input row, produce a verifiable record: `category` is one of the ten allowed strings;
  `priority` is Urgent when severity keywords appear in `description`, otherwise Standard or Low as
  applicable; `reason` is a single sentence that quotes or paraphrases specific words from
  `description`; `flag` is exactly `NEEDS_REVIEW` when category choice is genuinely ambiguous, else
  empty. Batch runs write `results_[city].csv` with no invented columns beyond the agreed schema.

context: >
  Allowed inputs: CSV rows from `../data/city-test-files/test_[city].csv` with columns such as
  `complaint_id`, `date_raised`, `city`, `ward`, `location`, `description`, `reported_by`, `days_open`.
  The ground-truth `category` and `priority_flag` columns are omitted from test files; classification
  must infer category and priority from `description` (and identifiers like `complaint_id` for output
  correlation only). Excluded: web search, ward knowledge not in the row, assumptions about undisclosed
  injuries or events.

enforcement:
  - "category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other — no abbreviations or alternate spellings."
  - "priority must be Urgent if description (case-insensitive) contains any of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse; otherwise use Standard or Low consistent with skills.md."
  - "reason must be one sentence and cite specific words or short phrases taken from the complaint description."
  - "If the complaint text does not support a single clear category, set category to Other and flag to NEEDS_REVIEW; never guess a specific category with high confidence when evidence is ambiguous."
