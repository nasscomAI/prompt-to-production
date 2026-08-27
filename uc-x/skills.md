# skills.md — UC-X Ask My Documents
skills:
  - name: retrieve_documents
    description: Loads policy files (HR, IT, Finance) and indexes them by document name and section number for precise retrieval.
    input: List of file paths to policy .txt files.
    output: Indexed document content (e.g., dictionary of sections mapped to text).
    error_handling: Refuses to index files with invalid formats or missing section markers.

  - name: answer_question
    description: Searches the indexed documents to find the single most relevant section, returning a citation-backed answer or the exact refusal template.
    input: String (user question) and Indexed document data.
    output: String (Answer + Source Citation or Refusal Template).
    error_handling: Returns the verbatim refusal template if no relevant section is found or if the answer requires blending multiple documents.
