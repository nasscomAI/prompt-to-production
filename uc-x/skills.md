# skills.md

skills:
  - name: retrieve_documents
    description: Loads and indexes all three policy files (HR, IT, Finance) by document name and section number for precise retrieval.
    input: List of paths to policy .txt files.
    output: An indexed collection of document sections.
    error_handling: Logs an error and skips any file that cannot be loaded.

  - name: answer_question
    description: Searches the indexed documents for a single-source match to provide a grounded answer with citations or a strict refusal.
    input: User query string and the indexed document collection.
    output: A single-source answer string with citations OR the verbatim refusal template.
    error_handling: Returns the exact refusal template if no direct, single-source evidence is found or if blending is required.
