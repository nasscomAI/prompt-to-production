skills:

name: classify_complaint
description: Classifies a single citizen complaint description into category, priority, reason, and review flag.
input: One complaint row as a dictionary containing at least complaint_id and description fields.
output: A dictionary with fields complaint_id, category, priority, reason, and flag.
error_handling: If the description is missing or ambiguous, assign category "Other" and set flag "NEEDS_REVIEW". The function must still return a valid output structure.

name: batch_classify
description: Reads a complaint CSV file, applies classify_complaint to each row, and writes the classification results to an output CSV file.
input: Path to an input CSV file containing complaint rows with descriptions.
output: A results CSV file containing complaint_id, category, priority, reason, and flag for every row.
error_handling: If a row is malformed or causes an exception, the row is still written with category "Other", priority "Low", reason describing the error, and flag "NEEDS_REVIEW" so processing continues without crashing.

