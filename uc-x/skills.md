skills:
  - name: retrieve_documents
    description: Ingests the three target policy text files and indexes their content by document name and section number for precise retrieval.
    input: List of strings (file paths to the policy documents).
    output: A structured dictionary or index mapping document names and section IDs to their corresponding text content.
    error_handling: If a document is missing or inaccessible, it halts the system and reports the specific file failure to ensure no partial (and thus potentially misleading) answers are generated.

  - name: answer_question
    description: Analyzes a user query against the document index to provide a single-source answer with citations or the mandatory refusal template.
    input: User query (string) and the indexed document structure.
    output: A string containing the direct answer + citation, or the exact refusal template if no clear single-source answer exists.
    error_handling: If the query spans multiple documents or triggers contradictory sections, it must prioritize the refusal template or report a conflict rather than blending information.
