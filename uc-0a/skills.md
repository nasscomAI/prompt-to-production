name: classify_complaint
description: Classifies a single complaint row into category, priority, reason, and flag based on the predefined schema.

input:
type: row
format: "Single CSV row containing complaint description text"

output:
type: row
format: "CSV row with fields: category (Pothole|Flooding|Streetlight|Waste|Noise|Road Damage|Heritage Damage|Heat Hazard|Drain Blockage|Other), priority (Urgent|Standard|Low), reason (one sentence citing words from description), flag (NEEDS_REVIEW or blank)"

error_handling:
"If complaint description is missing or empty, refuse to classify the row and return an error"
"If category cannot be mapped to exact allowed values, reject and remap strictly to the predefined list"
"If any severity keyword (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse) is present and priority is not Urgent, override to Urgent"
"If reason is missing or does not cite exact words from the description, return an error"
"If complaint is ambiguous between categories, set flag to NEEDS_REVIEW instead of guessing"
"Do not create or use any categories outside the allowed list (prevent taxonomy drift and hallucinated sub-categories)"
"If classification confidence is low, enforce NEEDS_REVIEW flag instead of confident assignment"


name: batch_classify
description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes the results to an output CSV.
input:
type: file
format: "CSV file located at ../data/city-test-files/test_[your-city].csv with 15 complaint rows"
output:
type: file
format: "CSV file written to uc-0a/results_[your-city].csv with fields: complaint_id, category, priority, reason, flag for each row"
error_handling:
"If input CSV file is missing, malformed, or unreadable, refuse processing and return an error"
"If any row is missing a complaint description, mark as error and halt or skip based on strict validation"
"Ensure all rows use only allowed category and priority values; reject any deviations"
"Enforce that rows containing severity keywords are always labeled Urgent"
"If any row is ambiguous, set flag to NEEDS_REVIEW instead of forcing classification"
"If reason field is missing or not one sentence citing description text, regenerate or fail"
"Prevent taxonomy drift by enforcing consistent use of predefined categories across all rows"
"Maintain exact row count between input and output, ensuring complaint_id integrity"
"If any enforcement rule cannot be satisfied, halt batch processing and return an error"
