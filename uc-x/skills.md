skills:

* name: retrieve_documents
description: Loads all 3 policy files and indexes their content by document name and section number.
input:
type: file_paths
format: list of strings (e.g., ["../data/policy-documents/policy_hr_leave.txt", "../data/policy-documents/policy_it_acceptable_use.txt", "../data/policy-documents/policy_finance_reimbursement.txt"])
output:
type: indexed_dataset
format: JSON object containing document names, section numbers, and corresponding text sections
error_handling: If any file path is missing or unreadable, throw a FileNotFoundError and halt execution; if section formatting is ambiguous, log a warning and fallback to default section splitting.
* name: answer_question
description: Searches the indexed policy documents and returns a single-source answer with citations or the exact refusal template.
input:
type: user_query
format: string (e.g., "Can I carry forward unused annual leave?")
output:
type: text_response
format: string containing a single-source answer with document name and section number citation, OR the exact refusal template
error_handling: If the query cannot be answered from a single document, requires cross-document blending, contains missing conditions, or is not covered in the documents, output the exact refusal template verbatim without using hedging phrases.