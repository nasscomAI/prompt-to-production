# skills.md

skills:
  - name: retrieve_documents
    description: Loads the HR, IT, and Finance policy documents and indexes them by document name and section number for easy retrieval.
    input: None.
    output: A collection of document sections with metadata (document name, section number, content).
    error_handling: If a document is missing, it should log an error and proceed with available documents if possible.

  - name: answer_question
    description: Searches the indexed policy documents to find a single-source answer to a user's question, providing citations.
    input: A user's question (string).
    output: A string containing the answer with document and section citation, or the refusal template if no answer is found.
    error_handling: If no single document provides a clear answer, or if information is ambiguous, it must return the exact refusal template.
