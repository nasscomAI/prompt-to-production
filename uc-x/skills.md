# UC-X — Ask My Documents

skills:

- name: retrieve_documents
  description: >
    Loads the three required CMC policy documents and indexes their
    subsections by document name and section number.
  input: >
    Policy directory path as a string.
  output: >
    Dictionary mapping each policy document name to a dictionary of
    section numbers and their corresponding section text.
  error_handling: >
    Raises FileNotFoundError if any required policy document is missing.
    Does not use external documents or information.

- name: answer_question
  description: >
    Matches an employee question to a supported single-source policy
    section and returns the source text with a document and section
    citation, or the exact refusal template when the question is not
    sufficiently supported.
  input: >
    Employee question as a string and the indexed policy documents
    returned by retrieve_documents.
  output: >
    A string containing the policy answer and its source document and
    section citation, or the exact refusal template.
  error_handling: >
    Refuses when no supported policy concept is identified, when the
    evidence is ambiguous, or when answering would require combining
    information from multiple documents or sections. It must not guess
    or use outside knowledge.