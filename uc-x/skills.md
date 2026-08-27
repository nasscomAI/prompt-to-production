skills:

- name: retrieve_documents
  description: Loads and indexes all policy documents by name and content.
  input: File paths of policy documents.
  output: Dictionary mapping document names to content.
  error_handling:
  If any file is missing, return error and empty dataset.

- name: answer_question
  description: Searches documents and returns answer from a single source with citation.
  input: User question and indexed documents.
  output: Answer with document name and section OR refusal template.
  error_handling:
  If answer is not clearly found in one document, return refusal template exactly.
