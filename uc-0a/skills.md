* name: classify_complaint
  description: Classifies a single civic complaint into category, priority, reason, and flag based strictly on the predefined schema.
  input:
  type: object
  format: "Single complaint row containing a free-text description field."
  output:
  type: object
  format: "{ category: one of [Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other], priority: one of [Urgent, Standard, Low], reason: one sentence citing exact words from the description, flag: NEEDS_REVIEW or blank }"
  error_handling:

  * "If the complaint text is missing or empty, return category as Other, priority as Low, reason indicating missing description, and flag as NEEDS_REVIEW."
  * "If the complaint cannot be confidently mapped to a single allowed category, set flag to NEEDS_REVIEW and avoid guessing."
  * "If severity keywords (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse) are present but priority is not Urgent, override to Urgent."
  * "If a category outside the allowed list is generated, replace it with Other and set flag to NEEDS_REVIEW."
  * "If reason cannot cite exact words from the description, regenerate reason to include explicit quoted terms from the input."
  * "Prevent taxonomy drift by enforcing exact category strings across all outputs."
  * "Avoid hallucinated sub-categories by restricting outputs strictly to the allowed category list."

* name: batch_classify
  description: Processes an input CSV of complaint rows, applies classify_complaint to each row, and writes a structured output CSV.
  input:
  type: file
  format: "CSV file at ../data/city-test-files/test_[your-city].csv containing 15 rows with complaint descriptions and no category or priority_flag columns."
  output:
  type: file
  format: "CSV file at uc-0a/results_[your-city].csv where each row includes category, priority, reason, and flag fields populated per schema."
  error_handling:

  * "If the input file is missing, unreadable, or malformed, abort processing and return an explicit error message."
  * "If any row is invalid or missing a description, process it using classify_complaint fallback (Other, Low, NEEDS_REVIEW)."
  * "Ensure all output rows contain all required fields; if any field is missing, regenerate that row."
  * "Maintain consistent category naming across rows to prevent taxonomy drift."
  * "Ensure severity keywords in any row trigger Urgent priority; correct any violations during processing."
  * "If ambiguous complaints are classified without NEEDS_REVIEW, reprocess and set the flag appropriately."
  * "Do not introduce new columns or omit required ones in the output CSV."
