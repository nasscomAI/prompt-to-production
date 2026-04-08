skills:
  - name: retrieve_documents
    description: Load policy documents and index them by document name and section number.
    input: File paths of the three policy text files.
    output: Dictionary of documents mapped to section numbers and text content.
    error_handling: If a document cannot be loaded or parsed, terminate execution and display an error.

  - name: answer_question
    description: Search indexed documents and return a single-source answer with document citation.
    input: User question string and indexed policy documents.
    output: Answer text with document name and section number citation or the refusal template.
    error_handling: If no relevant clause is found, return the refusal template exactly without modification.