# skills.md

skills:
  - name: retrieve_documents
    description: Load the three policy documents and index their contents by document name and section number.
    input: Three policy document files from data/policy-documents.
    output: Dictionary mapping each document name to its section-numbered policy text.
    error_handling: Raise an error if a required policy document is missing or cannot be read.

  - name: answer_question
    description: Search the indexed policy documents and return a single-source answer with citation or the exact refusal template.
    input: A user policy question as a string and the indexed policy documents.
    output: A precise policy answer with source document and section citation, or the exact refusal template.
    error_handling: Refuse when the question is not covered, is ambiguous, requires combining documents, or cannot be supported by exactly one policy document.
