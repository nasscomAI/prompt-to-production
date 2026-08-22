# skills.md — UC-X Skills Definition

skills:
  - name: retrieve_documents
    description: Reads all 3 policy text files from the data directory and indexes sections by document name and section number.
    input: List of file paths to policy documents.
    output: Indexed dictionary mapping `(document_name, section_number)` to text content.
    error_handling: Raises FileNotFoundError if any policy document path is invalid.

  - name: answer_question
    description: Searches the indexed policy documents, evaluates query relevance, and returns a single-source cited answer or the exact refusal template.
    input: User query string and indexed document collection.
    output: String response containing factual answer + section citation OR the exact refusal template.
    error_handling: Automatically outputs the refusal template if no exact policy match is found or if query requires cross-document speculative blending.

