skills:

name: classify_complaint
description: Classify one citizen complaint row using the defined category and priority taxonomy, provide a grounded reason, and flag genuinely ambiguous cases for review.
input:
type: complaint row
format: One complaint row containing a complaint description.
output:
type: classified complaint
format:
category: "One exact value from Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other"
priority: "One exact value from Urgent, Standard, Low"
reason: "Exactly one sentence citing specific words from the complaint description"
flag: "NEEDS_REVIEW or blank"
error_handling: "If the category is genuinely ambiguous, set flag to NEEDS_REVIEW rather than making a confident classification; always use exact allowed category strings, trigger Urgent for any severity keyword, and include a one-sentence reason citing specific words from the description."
name: batch_classify
description: Read an input CSV, classify every complaint row using classify_complaint, and write the classified results to an output CSV.
input:
type: CSV file
format: "Input CSV at ../data/city-test-files/test_[your-city].csv containing 15 complaint rows per city with category and priority_flag columns stripped."
output:
type: CSV file
format: "Classified CSV at uc-0a/results_[your-city].csv containing category, priority, reason, and flag for each complaint row."
error_handling: "For invalid or ambiguous complaint data, apply classify_complaint rules, use NEEDS_REVIEW for genuinely ambiguous categories, never invent sub-categories or vary taxonomy