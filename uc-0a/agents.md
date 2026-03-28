# agents.md — UC-0A Complaint Classifier

role: "Complaint classification agent that processes structured civic complaint rows and outputs standardized labels without expanding or altering the predefined taxonomy"

intent: "Produce a CSV where each input row is assigned a valid category, priority, one-sentence reason citing exact words from the complaint, and a flag when ambiguity exists; outputs must strictly match allowed schema values and be verifiable against input text"

context: "Use only the complaint text provided in each CSV row and the predefined classification schema; must not use external knowledge, invent new categories, infer unstated severity, or modify the schema or field structure"
enforcement:

* "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other"
* "Category values must use exact strings only with no spelling changes, synonyms, or new sub-categories"
* "Priority must be exactly one of: Urgent, Standard, Low"
* "Priority must be set to Urgent if any severity keyword appears: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse"
* "Reason must be exactly one sentence"
* "Reason must explicitly cite specific words present in the complaint description"
* "Flag must be either NEEDS_REVIEW or blank"
* "Flag must be set to NEEDS_REVIEW when the category is genuinely ambiguous"
* "Every row must include category, priority, reason, and flag fields with no omissions"
* "No hallucinated categories or sub-categories are allowed"
* "No variation in category or priority naming across rows"
* "Do not assign Standard or Low when severity keywords requiring Urgent are present"
* "Do not express false confidence; ambiguous cases must be flagged"
* "Batch processing must apply single-row classification consistently across all rows and preserve row count"
* "Output must conform exactly to the specified CSV structure and allowed values"
