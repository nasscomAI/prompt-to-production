# skills.md - UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes their content by document name and section number.
    input: List of file paths pointing to the policy text documents.
    output: An indexed knowledge base dictionary mapping document names and section numbers to text content.
    error_handling: If a document cannot be loaded, notify the user which specific file is missing.

  - name: answer_question
    description: Searches the indexed documents and returns a clean, single-source answer with citations or the exact refusal template.
    input: The user's question as a string, and the indexed knowledge base.
    output: An exact string answer citing a specific document and section, or the exact refusal template text.
    error_handling: If query matches across multiple documents creating ambiguity, or if the answer isn't fully contained in one, immediately return the standard refusal template.
