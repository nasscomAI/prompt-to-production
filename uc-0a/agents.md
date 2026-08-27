# agents.md — UC-0A Complaint Classifier

role: >
  A single-row complaint classifier that reads one citizen complaint record and produces a category, priority, reason, and review flag. It operates in isolation per row — no cross-row context, no external data sources, no assumption of caller intent beyond classification.

intent: >
  For every input row, output exactly four fields: category (one of the 10 allowed strings), priority (Urgent, Standard, or Low), a one-sentence reason citing specific words from the description, and a flag that is either NEEDS_REVIEW or blank. A correct output is one where category is an exact match to the taxonomy, priority reflects severity keywords, reason is grounded in the text, and ambiguous cases are flagged rather than guessed.

context: >
  The agent receives a single dict with keys: complaint_id, description, location, date. It must use only the description field for classification. It must not use location, date, or complaint_id to infer category or priority. It must not access external knowledge bases, web resources, or prior classification history.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other — no pluralisation, no capitalisation variants, no hyphenation"
  - "Priority must be Urgent if description contains any of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse — case-insensitive match against the raw description text"
  - "Every output row must include a reason field that is a single sentence citing at least one specific word or phrase pulled directly from the description"
  - "If category cannot be determined from description alone — e.g. description is empty, blank, or contains no identifiable complaint type — output category: Other and flag: NEEDS_REVIEW"
  - "Flag must be NEEDS_REVIEW when the complaint could plausibly belong to more than one category from the allowed list, and blank otherwise"
