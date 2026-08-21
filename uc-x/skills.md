# skills.md

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number.
    input: None (predefined paths for HR, IT, and Finance policies)
    output: List of document objects or sections with searchable text and metadata.
    error_handling: Return error message if files are missing or inaccessible.

  - name: answer_question
    description: Searches indexed documents to return a single-source answer with citation or the verbatim refusal template.
    input: query (string), indexed_documents (data structure)
    output: String containing evidence-based answer + citation (Doc + Section) OR refusal template.
    error_handling: Must return the verbatim refusal template if the answer requires cross-document blending, hedging, or is not found.
