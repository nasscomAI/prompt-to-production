# skills.md
skills:

name: classify_complaint
description: Classifies a single citizen complaint into category, priority, reason, and flag according to the schema.
input: |
Type: JSON object
Format: {
"description": "string containing complaint text"
}
output: |
Type: JSON object
Format: {
"category": "one of allowed values",
"priority": "Urgent | Standard | Low",
"reason": "one sentence citing words from description",
"flag": "NEEDS_REVIEW or blank"
}
error_handling: |
If input is invalid, ambiguous, or matches a failure mode:

Taxonomy drift: reject and return flag NEEDS_REVIEW.

Severity blindness: enforce Urgent when severity keywords appear.

Missing justification: return error message and require reason field.

Hallucinated sub-categories: reject and return flag NEEDS_REVIEW.

False confidence on ambiguity: set flag NEEDS_REVIEW instead of forcing category.

name: batch_classify
description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes results to output CSV.
input: |
Type: CSV file path
Format: "../data/city-test-files/test_[city].csv"
output: |
Type: CSV file
Format: "uc-0a/results_[city].csv" with columns [category, priority, reason, flag]
error_handling: |
If input file is missing or malformed, stop with a clear error. For rows with
an empty description, emit Other with NEEDS_REVIEW rather than silently
classifying the row.

Enforce schema rules across all rows to prevent taxonomy drift.

Ensure severity keywords trigger Urgent priority.

Require reason field for every row; if missing, mark as error.

Reject hallucinated categories and set flag NEEDS_REVIEW.

For ambiguous rows, set flag NEEDS_REVIEW instead of forcing classification.