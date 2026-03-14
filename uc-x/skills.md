skills:
  - name: retrieve_documents
    description: Loads and indexes the policy documents by document name and section number.
    input: File paths to the three policy documents.
    output: Dictionary mapping document names to their text content and sections.
    error_handling: If a document cannot be loaded, raise an error and stop execution.

  - name: answer_question
    description: Searches the indexed policy documents and returns a single-source answer with citation.
    input: User question string and indexed policy documents.
    output: Answer text with document name and section citation or the refusal template.
    error_handling: If the answer is not clearly found in one document, return the refusal template.