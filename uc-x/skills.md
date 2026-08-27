# skills.md — UC-X Policy Librarian Skills

skills:
  - name: retrieve_documents
    description: Loads all policy text files and parses them into a structured index organized by document name and section number.
    input: None (uses hardcoded paths to HR, IT, and Finance policies).
    output: Dictionary mapping document names to section identifiers and their respective content.
    error_handling: Reports missing files and ensures the index is only populated with valid, readable data.

  - name: answer_question
    description: Researches the indexed policy documents to find a single-source answer for a user's query, ensuring citations are included and hallucinations are avoided.
    input: String (user query) and the Document Index.
    output: String (cited answer or the mandatory refusal template).
    error_handling: If no single source provides a clear answer, or if information would need to be blended, it defaults to the refusal template.
