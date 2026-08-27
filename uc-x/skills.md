skills:

* name: retrieve_documents
description: Loads all three company policy files and indexes their contents by document name and section number.
input:
type: file_paths
format: List of string file paths (`../data/policy-documents/policy_hr_leave.txt`, `../data/policy-documents/policy_it_acceptable_use.txt`, `../data/policy-documents/policy_finance_reimbursement.txt`).
output:
type: document_index
format: Structured object mapping document names and section numbers to their text content.
error_handling: If any file path is missing, unreadable, or invalid, the skill raises a FileNotFoundError and halts execution without creating an incomplete index.
* name: answer_question
description: Searches indexed policy documents to return a single-source answer with citations or the exact refusal template.
input:
type: query_and_index
format: Object containing `question` (string) and `index` (document_index object from retrieve_documents).
output:
type: text_response
format: String containing a single-source answer with document name and section number citations, or the exact refusal template.
error_handling: |
If the question is unanswerable, not covered, or creates cross-document ambiguity/blending (e.g., combining claims across IT and HR documents), the skill immediately returns the exact refusal template verbatim: "This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact HR Support Team for guidance."