skills:
  - name: retrieve_documents
    description: Loads the three policy documents and indexes their sections for search.
    input: Paths to policy text files.
    output: Dictionary mapping document names to their policy text content.
    error_handling: If any document cannot be loaded, return an error and stop execution.

  - name: answer_question
    description: Searches the indexed policy documents and returns a single-source answer with citation.
    input: User question and indexed policy documents.
    output: Policy answer with document name and section citation, or the refusal template.
    error_handling: If the question is not found in any document, return the refusal template exactly.