skills:
  - name: retrieve_documents
    description: Load all policy documents and index them by document name and section number.
    input: Folder path containing policy .txt files.
    output: Dictionary mapping document names to text sections.
    error_handling: If files cannot be loaded, return an error and stop execution.

  - name: answer_question
    description: Search indexed policy documents and return a single-source answer with citation.
    input: User question string and indexed policy documents.
    output: Answer text with document name and section citation, or the refusal template.
    error_handling: If the question is not found in any document, return the refusal template exactly.