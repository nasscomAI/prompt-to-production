skills:
- name: retrieve_documents
  description: Load all three policy files and index their numbered sections by document name.
  input: Three policy document file paths.
  output: Structured document index containing document names, section numbers, and source text.
  error_handling: If a document cannot be loaded, report the missing document rather than inventing its contents.
- name: answer_question
  description: Answer a policy question using one source document and provide an exact section citation or return the required refusal template.
  input: User policy question and indexed policy documents.
  output: Single-source answer with document and section citation, or the exact refusal template.
  error_handling: Refuse when the question is not covered or would require combining claims from multiple documents.
