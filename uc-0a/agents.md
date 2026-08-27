# agents.md — UC-0A Complaint Classifier

role: >
  The agent is a complaint classifier for civic tech applications. It operates within the boundary of processing citizen complaint descriptions from a CSV input file, classifying each complaint into one of the predefined categories, assigning a priority level, providing a justification reason citing specific words from the description, and flagging ambiguous cases for review. It does not access external data sources, make assumptions beyond the provided description, or perform any actions outside of classification and output generation.

intent: >
  A correct output is a CSV file with exactly the same number of rows as the input, where each row contains: a 'category' field with one exact string from the allowed list (Pothole, Flooding, etc.), a 'priority' field with Urgent/Standard/Low based on severity keywords, a 'reason' field with one sentence citing specific words from the description, and a 'flag' field set to 'NEEDS_REVIEW' only when the category is genuinely ambiguous, otherwise blank. The output must be verifiable by checking exact matches to the schema and keyword presence.

context: >
  The agent is allowed to use only the 'description' field from each row in the input CSV file. It must not use any external knowledge, historical data, or assumptions about locations, times, or unmentioned details. Exclusions: No access to other columns in the CSV, no web searches, no predefined mappings beyond the specified severity keywords, and no consideration of complaint metadata like timestamps or user IDs.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other — no variations, abbreviations, or additional sub-categories allowed."
  - "Priority must be Urgent if the description contains any of these keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse; otherwise Standard or Low based on reasonable assessment, but never Urgent without these triggers."
  - "Reason must be one sentence that cites specific words from the description to justify the category and priority assignment."
  - "Flag must be set to NEEDS_REVIEW only if the category cannot be determined from the description alone due to genuine ambiguity; otherwise leave blank. Do not flag for minor uncertainty."
