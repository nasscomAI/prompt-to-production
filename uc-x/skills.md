skills:
  - name: retrieve_documents
    description: Loads and indexes all policy text files by document name and numbered section clauses.
    input: List of policy document file paths.
    output: Structured index mapping document names and section numbers to raw text paragraphs.
    error_handling: Handles missing policy files gracefully, raising FileNotFoundError if any input document is missing.

  - name: answer_question
    description: Analyzes user query against indexed policy sections and generates single-source answers with exact citations or exact refusal template.
    input: User query string and indexed policy document dictionary.
    output: Formatted text response containing factual policy answer with document and section citation, or exact refusal message.
    error_handling: Refuses immediately using exact refusal template if no matching policy section addresses the query.
