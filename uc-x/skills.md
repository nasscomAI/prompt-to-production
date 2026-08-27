
name: retrieve_documents
description: Loads all three policy documents and indexes their contents by document name and section number.
input:
type: none
format: no input required; loads predefined file paths
output:
type: structured_index
format: mapping of document_name -> section_number -> text content
error_handling:

If any file is missing or unreadable, return an error indicating which document failed to load
If document structure lacks clear section numbers, return an error indicating invalid document format
Do not attempt to infer or reconstruct missing sections or content



name: answer_question
description: Searches indexed policy documents and returns a single-source answer with citation or the exact refusal template.
input:
type: string
format: natural language question
output:
type: string
format: either a single-source answer with document name and section citation or the exact refusal template
error_handling:

If no relevant answer is found in any document, return exactly: "This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."
If answering requires combining information from multiple documents, return the exact refusal template
If multiple sections within the same document create ambiguity, return the exact refusal template
Do not generate answers containing hedging phrases such as "while not explicitly covered", "typically", "generally understood", or "it is common practice"
If input is empty, invalid, or nonsensical, return the exact refusal template
Do not provide partial answers if document conditions or constraints are incomplete
