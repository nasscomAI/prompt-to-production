skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number.
    input: List of file paths to the policy documents.
    output: A structured index mapping document names to their respective numbered sections.
    error_handling: If any document is missing or unreadable, log an error and omit it from the index rather than failing completely.

  - name: answer_question
    description: Searches indexed documents and returns a single-source answer with a citation, or the exact refusal template.
    input: The user's question string and the structured index.
    output: A factual answer citing a single source document and section, or the exact refusal template.
    error_handling: If the answer requires blending information from multiple documents, or if the answer is not explicitly present, immediately return the exact refusal template without any hedging.
