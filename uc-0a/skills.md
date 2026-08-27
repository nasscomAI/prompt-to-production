
skills:

name: classify_complaint
description: Classifies a single municipal complaint into a predefined category and assigns priority.
input: A complaint record containing a description field (string).
output: category (string), priority (string), reason (string), flag (string).
error_handling: If the complaint cannot be clearly categorized from the description, assign category Other and set flag to NEEDS_REVIEW.

name: batch_classify
description: Processes a CSV file of complaints and applies classify_complaint to each row.
input: CSV file containing complaint records with a description column.
output: CSV file containing classification results with fields category, priority, reason, and flag.
error_handling: If a row is missing description or contains invalid input, classify it as category Other and set flag to NEEDS_REVIEW.