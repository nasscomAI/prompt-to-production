skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number for storage and retrieval.
    input: Path to policy-documents directory (string).
    output: Indexed document structure (JSON/Object).
    error_handling: Fail if any specific document or directory is missing.

  - name: answer_question
    description: Searches the indexed policy documents to provide a single-source answer with citations or a refusal.
    input: User policy-related string query.
    output: String (answer with citation [Document, Section] or verbatim refusal template).
    error_handling: Output the refusal template if the query cannot be answered by a single source or is not found.
