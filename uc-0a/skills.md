# skills.md

1. name: classify_complaint
  description: Classifies a single civic complaint into category, priority, reason, and flag based strictly on the predefined schema and rules.
  input:
  type: string
  format: "One complaint description text from a CSV row"
  output:
  type: object
  format: "category (string), priority (string), reason (one sentence string), flag (string or blank)"
  error_handling: >
  If the input is empty or not a valid string, return an error and do not classify; if category mapping is unclear, assign the closest valid category and set flag to NEEDS_REVIEW; if ambiguity exists between multiple categories, set flag to NEEDS_REVIEW; if severity keywords are present, always override priority to Urgent; never generate categories outside the allowed list; if unable to produce a one-sentence reason citing input text, return an error to avoid missing justification; ensure consistency to prevent taxonomy drift and avoid false confidence.

2. name: batch_classify
  description: Processes an input CSV file of complaints, applies classify_complaint to each row, and writes a structured output CSV file.
  input:
  type: file path
  format: "../data/city-test-files/test_[your-city].csv containing 15 complaint rows without category and priority_flag columns"
  output:
  type: file path
  format: "uc-0a/results_[your-city].csv with category, priority, reason, and flag columns for each row"
  error_handling: >
  If the input file is missing, unreadable, or improperly formatted, return an error and halt processing; if any row is invalid or empty, skip classification for that row and log an error; ensure output row count matches input row count; propagate NEEDS_REVIEW flags from classify_complaint for ambiguous cases; prevent schema violations such as invalid categories or missing fields; enforce urgency rules to avoid severity blindness; ensure every row includes a valid reason to avoid missing justification.
