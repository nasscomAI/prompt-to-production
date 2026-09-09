skills:
  - name: retrieve_documents
    description: Loads all available policy documents and builds a structured, section-indexed catalog for precise citation retrieval.
    input: List of document file paths or directory containing policy documents (HR, IT, Finance).
    output: Indexed mapping of document names, sections, clauses, and text bodies.
    error_handling: Raises FileNotFoundError if any required policy document is missing; logs parsing warnings for malformed sections.

  - name: answer_question
    description: Answers citizen or employee inquiries strictly using single-source attribution or returns the mandatory refusal template.
    input: Question string (query) and indexed policy document catalog.
    output: String containing single-source factual answer with document and section citation, or the exact refusal template with relevant team contact placeholder.
    error_handling: Detects cross-document blending hazards or questions not covered by the policies, suppressing hallucinated or hedged responses and returning the strict refusal template.
