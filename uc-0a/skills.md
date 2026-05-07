# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:

name: classify_complaint
description: Evaluates a single citizen complaint to assign a strict category, priority, justification, and review flag.
input:
type: object
format: A single complaint record containing a text description.
output:
type: object
format: Four strict fields containing category, priority, reason, and flag.
error_handling: Sets the flag to NEEDS_REVIEW if ambiguous to prevent false confidence, maps unrecognized concepts strictly to Other to prevent hallucinated sub-categories and taxonomy drift, and forces Urgent priority if any severity keyword is present to prevent severity blindness.

name: batch_classify
description: Reads an input CSV file, applies the classify_complaint skill to each row, and writes the results to an output CSV.
input:
type: string
format: File path to the input CSV.
output:
type: string
format: File path to the output CSV.
error_handling: Halts execution if the input CSV cannot be read, and assigns a blank reason with a NEEDS_REVIEW flag if an individual row is entirely malformed or fails the underlying classification schema.