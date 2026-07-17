# skills.md — UC-X Policy Q&A

skills:
  - name: retrieve_documents
    description: Loads the three policy documents and indexes their section content for lookup by question.
    input: The base directory containing the data/policy-documents folder.
    output: A dictionary mapping document names to their full text.
    error_handling: If a document is missing, return only the documents that are available and refuse unsupported questions.

  - name: answer_question
    description: Searches the indexed documents, returns a single-source answer with citation, or uses the refusal template if the question is not covered.
    input: A user question string and the indexed documents.
    output: A plain-text answer containing either a factual answer with a citation or the refusal template.
    error_handling: If the question cannot be answered from a single document, return the refusal template rather than blending sources.
