# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Reads and indexes policy files (HR, IT, Finance) by document name and section number.
    input: List of policy document file paths.
    output: Indexed dictionary of section text with source metadata.
    error_handling: Raises error if any required policy document is missing.

  - name: answer_question
    description: Matches user question against indexed policy sections and returns single-source answer with citations or exact refusal template.
    input: Question string and indexed policy documents.
    output: Formatted response string with document and section citation OR strict refusal text.
    error_handling: Outputs refusal template when question is unmentioned or ambiguous across documents.

