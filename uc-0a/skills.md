skills:

name: classify_complaint 
description: Classifies a single citizen complaint by mapping it to a category, priority, reason, and review flag. 
input: Dictionary representing one complaint row, containing the complaint description as a string. 
output: Dictionary containing category (exact allowed string), priority (Urgent/Standard/Low), reason (one sentence citing specific words), and flag (NEEDS_REVIEW or blank). 
error_handling: Set flag to NEEDS_REVIEW and category to Other if the complaint is genuinely ambiguous; automatically set priority to Urgent if severity keywords (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse) are present; and fail or fallback to category Other if the input is malformed.

name: batch_classify 
description: Processes a batch of citizen complaints by reading an input CSV, running classification row by row, and exporting to an output CSV. 
input: Paths to the input CSV file (string) containing unclassified complaint rows. 
output: Path to the generated output CSV file (string) containing the classified complaints with category, priority, reason, and flag columns. 
error_handling: Aborts batch execution and logs an error if the input CSV file is missing or unreadable; for individual row processing failures, it logs a warning and falls back to default values (category Other, priority Low, flag NEEDS_REVIEW) to avoid halting the entire batch.