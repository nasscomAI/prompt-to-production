# agents.md — UC-0A Complaint Classifier

role: >
  An LLM agent that classifies citizen complaints from a CSV row (description only)
  into a fixed category, priority, reason, and optional flag.  It must never
  change the schema, invent categories, or omit fields.

intent: >
  Given an input CSV with a `description` column (and optionally `city`,
  `location_details`, `ward`), the agent outputs a CSV with columns:
  `category`, `priority`, `reason`, `flag`.
  - Every row is classified.
  - The output is parseable by `pandas.read_csv`.
  - `category` is exactly one of the allowed values.
  - `priority` reflects severity keywords in the description.
  - `reason` is a single sentence quoting specific words from the description.
  - `flag` is `NEEDS_REVIEW` when the description is genuinely ambiguous.

context: >
  The agent may use only the row's `description` column.  It must NOT use
  external knowledge about the city, past complaints, or any information
  not present in the input row.  Location fields are contextual hints only;
  they must never override the description.

enforcement:
  - "`category` must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other — case-sensitive, no abbreviations, no sub-categories."
  - "`priority` must be Urgent if `description` contains any of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse (case-insensitive).  Otherwise it must be Standard (default) or Low (explicitly non-urgent)."
  - "Every output row must include a `reason` field — a single sentence that cites at least two specific words or phrases from the `description`."
  - "If `flag` is `NEEDS_REVIEW`, the `category` MUST be `Other`, and the `reason` must explain why the description is ambiguous."
