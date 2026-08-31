skills:
  - name: retrieve_documents
    description: Loads all three policy text documents and parses them into structured sections indexed by document name and section number.
    input: List or paths of policy files (strings).
    output: Structured index mapping document names and section identifiers to section text.
    error_handling: Raises FileNotFoundError if any document is missing; raises ValueError if any file cannot be parsed.

  - name: answer_question
    description: Searches the indexed policy documents for relevant sections, answers from a single authoritative section with citations, or returns the standard refusal template.
    input: Question string and indexed documents dictionary.
    output: String containing single-source factual answer with document and section citation, or exact refusal template.
    error_handling: Employs strict refusal template if question topic is absent, ambiguous, or tempts cross-document blending.