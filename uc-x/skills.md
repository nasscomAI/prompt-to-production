skills:
  - name: retrieve_documents
    description: Loads and indexes all mandatory policy files (HR, IT, Finance) by document name and section number for precise retrieval.
    input: None (internal loading of predefined policy files).
    output: An indexed collection of policy sections.
    error_handling: Logs a critical error if any of the mandatory policy files are missing from the designated data directory.

  - name: answer_question
    description: Searches indexed documents to provide single-source answers with citations or returns a standardized refusal template if the answer is not found.
    input: User question as a string.
    output: A single-source answer with document and section citations OR the standardized refusal template.
    error_handling: Uses the exact refusal template if no answer is found or if answering would require blending information from multiple documents in an ambiguous way.
