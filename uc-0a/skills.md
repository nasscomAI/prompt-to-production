skills:

* name: "classify_complaint"
  description: "Classifies one citizen complaint into an allowed category and priority while providing a description-grounded reason and ambiguity flag."
  input:
  type: "object"
  format: "One complaint row containing a description field from the input CSV."
  output:
  type: "object"
  format: "Fields: category, priority, reason, flag; category is exactly one of Pothole · Flooding · Streetlight · Waste · Noise · Road Damage · Heritage Damage · Heat Hazard · Drain Blockage · Other; priority is exactly one of Urgent · Standard · Low; reason is one sentence citing specific words from the description; flag is NEEDS_REVIEW or blank."
  error_handling:
  invalid_input: "Reject rows with a missing, empty, or unusable complaint description rather than fabricating a classification."
  ambiguous: "When the category is genuinely ambiguous, select the best supported allowed category and set flag to NEEDS_REVIEW instead of expressing false confidence."
  taxonomy_drift: "Use only the exact allowed category strings and never create variations or sub-categories."
  severity_blindness: "Set priority to Urgent whenever the description contains any of these severity keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse."
  missing_justification: "Always produce a one-sentence reason containing specific words from the complaint description."
  hallucinated_subcategories: "Map the complaint only to the defined category list and use Other when no defined category is supported."
  false_confidence: "Set NEEDS_REVIEW for genuinely ambiguous categories."

* name: "batch_classify"
  description: "Reads a complaint CSV, applies classify_complaint to every row, validates the results, and writes the classified rows to an output CSV."
  input:
  type: "file"
  format: "CSV file such as ../data/city-test-files/test_pune.csv containing complaint rows and their descriptions, with category and priority_flag stripped."
  output:
  type: "file"
  format: "CSV file such as uc-0a/results_pune.csv containing every input row with category, priority, reason, and flag classification fields."
  error_handling:
  invalid_input: "Reject the input if the CSV is missing, unreadable, malformed, empty, or lacks the complaint description field; do not fabricate rows or classifications."
  ambiguous: "Preserve classify_complaint's NEEDS_REVIEW handling for genuinely ambiguous rows rather than forcing confident classifications."
  taxonomy_drift: "Validate every output category against exactly Pothole · Flooding · Streetlight · Waste · Noise · Road Damage · Heritage Damage · Heat Hazard · Drain Blockage · Other and reject invalid variations."
  severity_blindness: "Validate every row so any occurrence of injury, child, school, hospital, ambulance, fire, hazard, fell, or collapse results in priority Urgent."
  missing_justification: "Reject output rows missing reason or containing a reason that is not exactly one sentence with specific words from the complaint description."
  hallucinated_subcategories: "Reject any category outside the exact allowed category list."
  false_confidence: "Reject or correct any genuinely ambiguous row that lacks the NEEDS_REVIEW flag."
  row_integrity: "Ensure every input complaint row receives exactly one category, priority, reason, and flag without silently dropping rows."

