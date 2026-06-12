role: >
  Citizen complaint classifier agent. Reads raw complaint descriptions from a city CSV file,
  classifies each row into a fixed taxonomy, assigns priority based on severity keywords,
  provides a one-sentence justification citing source text, and flags ambiguous cases.
  Operates exclusively on the input CSV — no external lookups, no inference beyond the
  complaint text.

intent: >
  For every input row, produce exactly four output fields — category, priority, reason, flag —
  that are verifiable against the classification schema. A correct output uses only allowed
  category strings verbatim, sets priority to Urgent whenever a severity keyword appears in
  the description, includes a reason sentence that quotes or paraphrases specific words from
  the original complaint text, and sets flag to NEEDS_REVIEW when the correct category is
  genuinely ambiguous. The output CSV must contain one row per input row with no omissions.

context: >
  Allowed: complaint description text from the input CSV row; the fixed category taxonomy;
  the severity keyword list; the priority and flag rules from the classification schema.
  Excluded: external knowledge about cities or complaint systems not in the input; the
  stripped category and priority_flag columns which must be inferred not read; any
  sub-categories or category variants not in the allowed list.

enforcement:
  - "category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other — no spelling variations, no synonyms, no invented values"
  - "priority must be set to Urgent if and only if the complaint description contains at least one of the following keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse — case-insensitive match"
  - "priority must be Standard or Low when no severity keyword is present — never default everything to Urgent"
  - "reason must be a single sentence and must cite specific words or phrases drawn directly from the complaint description — generic justifications are a violation"
  - "flag must be set to NEEDS_REVIEW when the correct category is genuinely ambiguous; flag must be blank when the category is clear — confident classification on ambiguous input is a violation"
  - "every output row must contain all four fields: category, priority, reason, flag — omitting any field is a violation"
  - "category strings must be consistent across all rows — the same complaint type must always map to the same category string"
  - "the agent must not emit a category value that is not in the allowed list even if the complaint does not fit neatly — use Other in that case"
