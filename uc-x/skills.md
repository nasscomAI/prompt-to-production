# skills.md

skills:
  - name: retrieve_documents
    description: Loads the three policy files and indexes them by document name and section number for fast retrieval.
    input: None.
    output: A collection of searchable document sections.
    error_handling: Log an error if any of the three files are missing or unreadable.

  - name: answer_question
    description: Searches the indexed documents and returns a clean, single-source answer with citations or the mandatory refusal template.
    input: User question (string).
    output: Final answer text with citations.
    error_handling: Return the exact refusal template if no clear single-source answer is found.
