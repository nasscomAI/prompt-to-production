skills:
  - name: retrieve_documents
    description: Loads all three policy files from ../data/policy-documents/ and indexes them by document name and section number.
    input: Directory containing the three policy text files
    output: Object mapping document names to dictionaries of section numbers and text content.
    error_handling: Return refusal template if documents cannot be loaded.

  - name: answer_question
    description: Searches the indexed documents for a question, returns a single-source answer with citation OR the exact refusal template.
    input: User's question and the index object from retrieve_documents
    output: String representing either a factual answer citing exactly one document.section, or the refusal template.
    error_handling: Return refusal template if multiple documents match, no documents match, or if hedging phrases are generated.