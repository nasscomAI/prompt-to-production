name: retrieve_policy
description: Loads an HR policy text file and parses the content into a structured list of numbered sections.
input:
type: string
format: File path to a .txt policy document.
output:
type: object
format: JSON object containing an array of numbered clauses and their raw text.
error_handling: Returns an error if the file is missing, unreadable, or if the text format lacks clear numerical clause identifiers required for mapping.

name: summarize_policy
description: Generates a condensed version of policy sections while strictly maintaining every condition, obligation, and clause reference without scope bleed.
input:
type: object
format: Structured list of numbered clauses and their original text.
output:
type: string
format: A compliant summary document where each entry corresponds to a source clause and includes all original constraints.
error_handling: Reverts to verbatim quotation and flags the section if a summary cannot be achieved without dropping conditions or softening binding verbs.
