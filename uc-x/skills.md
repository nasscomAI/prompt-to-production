skills:
  - name: retrieve_documents
    description: Loads all three policy files and indexes content by document name and numbered section.
    input: Base directory path containing the policy text files.
    output: Dictionary keyed by policy filename with parsed section-clause entries.
    error_handling: Raises explicit file-not-found or parse errors when required documents are unavailable or malformed.

  - name: answer_question
    description: Finds the best single-source policy answer with section citation, or returns the refusal template.
    input: Document index plus a natural-language user question.
    output: Single-source cited answer lines or exact refusal template string.
    error_handling: Refuses unanswered or cross-document-ambiguous questions and never fills gaps with external assumptions.
