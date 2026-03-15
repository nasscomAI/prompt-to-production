# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:

name: classify_complaint
description: Classifies a single complaint description into a valid category and assigns a priority level.
input: A dictionary representing one complaint row from the input CSV file.
output: A dictionary containing complaint_id, category, priority, reason, and flag.
error_handling: If the complaint description is missing or ambiguous, assign category "Other", set flag to "NEEDS_REVIEW", and still return a valid output row.

name: batch_classify
description: Reads an input CSV file of complaints, applies classify_complaint to each row, and writes the results to a new CSV file.
input: Input CSV file path and output CSV file path.
output: A results CSV file containing complaint_id, category, priority, reason, and flag.
error_handling: If a row cannot be processed due to malformed data, the row should still be written with category "Other" and flag "NEEDS_REVIEW" instead of stopping execution.
