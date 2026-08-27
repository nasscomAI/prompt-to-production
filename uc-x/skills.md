skills:
  - name: retrieve_documents
    description: >
      Loads and indexes policy documents by document name and section number.
    input: >
      List of file paths to policy documents.
    output: >
      Dictionary structured as {document_name: {section_number: section_text}}.
    error_handling: >
      Raises error if any file is missing or unreadable.
      Ignores malformed sections safely.

  - name: answer_question
    description: >
      Searches indexed policy documents and returns an answer strictly from a single source section or refusal.
    input: >
      Question string and indexed document dictionary.
    output: >
      Either a single-source answer with document name and section citation OR the refusal template.
    error_handling: >
      If multiple documents match → refuse (to prevent blending).
      If no match found → return refusal template exactly.
      Prevents partial matches and ambiguous answers.