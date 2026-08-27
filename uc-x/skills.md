# skills.md — UC-X Policy Librarian

skills:
  - name: retrieve_documents
    description: Loads and indexes all three policy documents (HR, IT, Finance) by document name and section number to facilitate precise retrieval.
    input: File paths to the mandated .txt policy documents.
    output: A structured index where each entry contains a unique document identifier, section number, and the verbatim text.
    error_handling: Reports an error if a primary document is missing; ensures no partial or corrupt indexing occurs.

  - name: answer_question
    description: Executes a single-source search across indexed documents to provide non-hedged answers with mandatory citations.
    input: User query string and the indexed document collection.
    output: A concise answer citing the source document and section, or the verbatim mandated refusal template if information is missing or requires blending.
    error_handling: If any ambiguity or multi-document dependency is detected, it must default to the refusal template rather than attempting to synthesize an answer.
