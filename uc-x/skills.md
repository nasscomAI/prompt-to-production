# skills.md — UC-X Policy Assistant

skills:
  - name: retrieve_documents
    description: Loads and indexes multiple policy documents by name and section for fast retrieval.
    input: List of paths to policy text files.
    output: An indexed knowledge base searchable by document and section.
    error_handling: Logs a warning if a file is unreadable but continues indexing remaining files.

  - name: answer_question
    description: Retrieves relevant sections and generates a single-source answer with citations or a refusal.
    input: A user question and the indexed knowledge base.
    output: A string containing the answer with document/section citations OR the strict refusal template.
    error_handling: Returns the exact refusal template if the information is not found or if the answer would require blending sources.
