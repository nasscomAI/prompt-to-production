- name: retrieve_documents
  description: >
    Loads all three policy files and indexes their numbered sections by
    document name and section number.
  input: >
    Three policy document paths in TXT format.
  output: >
    Structured collection containing document filename, section number,
    section title, and section text.
  error_handling: >
    If a document cannot be loaded, report the missing document and stop
    rather than answering from incomplete policy information.

- name: answer_question
  description: >
    Searches the indexed policy sections and returns a single-source
    policy answer with document and section citation, or the exact refusal
    template.
  input: >
    A user question as plain text and the indexed policy documents.
  output: >
    A policy answer citing exactly one source document and section, or the
    required refusal template.
  error_handling: >
    If no section clearly covers the question, or answering would require
    combining multiple documents, return the exact refusal template.
