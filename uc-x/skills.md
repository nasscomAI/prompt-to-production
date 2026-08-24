skills:
  - name: retrieve_documents
    description: Loads and indexes all three policy documents by filename and section number into a structured searchable knowledge store.
    input: List of policy document file paths.
    output: Indexed dictionary mapping document names and section IDs to section text and clauses.
    error_handling: Raises error if any policy file is missing or unreadable.

  - name: answer_question
    description: Processes a user query against indexed policy documents, returning a single-source answer with document name and section citation, or the exact refusal template.
    input: Query string and indexed policy documents store.
    output: Formatted string containing single-source answer with explicit section citation or exact refusal response.
    error_handling: Returns exact refusal template if query cannot be answered from a single source section or is not present in policy documents.
