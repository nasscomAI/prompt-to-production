skills:
name: classify_complaint
description: Classifies a single citizen complaint row into category, priority, reason, and flag.
input: |
One complaint row with description text (string).
output: |
Object with fields:
- category: one of [Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other]
- priority: Urgent, Standard, or Low
- reason: one sentence citing words from description
- flag: NEEDS_REVIEW or blank
error_handling: |
If description is ambiguous, set flag to NEEDS_REVIEW.
If severity keywords are present but priority is not Urgent, correct to Urgent.
If category is not in allowed list, set flag to NEEDS_REVIEW.
If reason is missing or not citing description words, regenerate with proper justification.
Prevent taxonomy drift, hallucinated sub-categories, and false confidence on ambiguity.
name: batch_classify
description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes results to output CSV.
input: |
CSV file at ../data/city-test-files/test_[your-city].csv with complaint rows (15 rows per city).
output: |
CSV file at uc-0a/results_[your-city].csv with columns: category, priority, reason, flag.
error_handling: |
If any row produces invalid category, mark flag NEEDS_REVIEW.
If severity blindness occurs, enforce Urgent priority for severity keywords.
If reason is missing, regenerate with one sentence citing description words.
If taxonomy drift or hallucinated sub-categories appear, correct to allowed categories.
If ambiguity is detected, set flag NEEDS_REVIEW instead of confident classification.