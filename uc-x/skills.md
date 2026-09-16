skills:
  - name: retrieve_documents
    description: Ingests and parses all three corporate policy documents (HR, IT, Finance) into structured sections and indexed text chunks tagged with document provenance.
    input: List of file paths to policy text files.
    output: Dictionary mapping document names to structured sections, section titles, and numbered clause texts.
    error_handling: Raises FileNotFoundError if any expected policy document is missing or empty.

  - name: answer_question
    description: Analyzes an employee query against indexed policies, extracts relevant provisions strictly from a single authoritative document, cites document and section, or outputs the verbatim refusal template.
    input: Query string (str) and structured policy index (dict).
    output: String response containing single-source factual answer with section citation, or exact refusal template.
    error_handling: Disallows multi-document blending; outputs verbatim refusal template when question is out of scope or ambiguous.
