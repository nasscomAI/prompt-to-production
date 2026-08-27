skills:
- name: retrieve_documents
  description: Loads and indexes approved policy documents by document name and section number.
  input: >
  policy_hr_leave.txt,
  policy_it_acceptable_use.txt,
  policy_finance_reimbursement.txt
  output: >
  Searchable index containing document names, sections and content.
  error_handling: >
  If a document is missing or unreadable, return an error and do not answer questions from that document.

- name: answer_question
  description: Answers policy questions using a single source document and section citation.
  input: >
  User question and indexed documents.
  output: >
  Single-source answer with citation or refusal template.
  error_handling: >
  If information is not found or requires cross-document blending,
  return the refusal template exactly.