skills:

name: retrieve_documents
description: Loads policy documents and indexes them by document name and section number.
input: File paths of policy documents.
output: Structured dictionary containing document sections.
error_handling: If a document cannot be loaded, return error message.

name: answer_question
description: Searches indexed documents and returns an answer from a single document section or the refusal template.
input: User question and indexed policy documents.
output: Answer with document name and section citation OR refusal template.
error_handling: If question is not covered, return refusal template exactly.

