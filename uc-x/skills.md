skills:
  - name: retrieve_documents
    description: Loads and indexes HR, IT, and Finance policy text files from the local data directory.
    input: Path to the policy-documents folder (String).
    output: Indexed document content categorized by filename and section (Object/Dictionary).
    error_handling: Returns an error message if any file is missing or the directory path is invalid.

  - name: answer_question
    description: Searches the indexed documents to provide a single-source answer with proper citation.
    input: User query (String) and Indexed documents (Object).
    output: Verified answer with Document Name and Section Number, or a specific refusal template (String).
    error_handling: If the query is ambiguous or not found in any document, it returns the mandatory refusal template.