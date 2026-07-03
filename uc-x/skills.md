skills:
name: retrieve_documents
description: Reads and parses target policy text files, indexing their content strictly by document name and section number.
input:
type: array
format: "List of file paths of target policy documents."
output:
type: object
format: "Structured mapping with document and section identifiers as keys and parsed clause content as values."
error_handling:
invalid_input: "Halt execution and report an error if any of the target policy files are missing, inaccessible, or contain no parsable sections."
ambiguous_input: "Log a warning for unreadable or unsupported file formats, parsing only accessible text sections."
failure_modes:
- "Maintain strict separation between documents during indexing to prevent future cross-document blending."
name: answer_question
description: Matches queries against indexed policy sections to yield a single-source response with citations or the unmodified refusal template.
input:
type: object
format: "A mapping that contains 'query' (string) and the indexed dictionary of document sections."
output:
type: string
format: "A factual answer appended with the source document and section citations, or the exact refusal template."
error_handling:
invalid_input: "If the query is blank, prompt the user for a valid question."
ambiguous_input: "If the query spans multiple conflicting policies or creates ambiguity, refuse and output the standard refusal template."
failure_modes:
- "If the question is not answered by the documents, output this exact refusal template without variations: 'This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance.'"
- "Enforce single-source answers with zero combination of distinct document claims and zero hedging."