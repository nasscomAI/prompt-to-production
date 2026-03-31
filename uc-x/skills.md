skills:
  - name: retrieve_documents
    description: Loads the policy documents and indexes the content by document name and section number for precise retrieval.
    input: List of file paths for policy documents.
    output: An indexed data structure mapping section identifiers to their literal text.
    error_handling: Error if any of the target policy files are missing or unreadable.

  - name: answer_question
    description: Searches the indexed documents for a query and returns a single-source answer with citations or the exact refusal template.
    input: User query (string), indexed documents.
    output: A string containing the cited answer or the specific refusal template.
    error_handling: If multiple documents contain conflicting or partial info, refuse to blend and instead provide separate cited answers or use the refusal template if ambiguity persists.
