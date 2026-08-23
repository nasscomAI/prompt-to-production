# skills.md

skills:
  - name: read_documents
    description: Reads policy documents from the dataset.
    input: Path to policy document folder.
    output: Dictionary of document names and text content.
    error_handling: If a document cannot be read, skip it and continue.

  - name: search_answer
    description: Searches documents to find relevant information for a user query.
    input: User question and document contents.
    output: Text answer and source document name.
    error_handling: If no answer is found, return INFORMATION_NOT_FOUND.