skills:
  - name: retrieve_documents
    description: Loads all 3 policy files from ../data/policy-documents/, indexes them by document name and section number, and returns the parsed content for use in answering questions.
    input: List of file paths (default: the 3 policy files in ../data/policy-documents/)
    output: Dictionary mapping document names to their section-structured content
    error_handling: If a file is missing or unreadable, raise a clear error listing which file could not be loaded and abort.

  - name: answer_question
    description: Searches the indexed policy documents for an answer to the user's question, returns a single-source answer with citation, or the verbatim refusal template if no document covers the question.
    input: User question (string)
    output: Answer string — either (A) single-source answer with document name + section citation, or (B) the exact refusal template
    error_handling: If question matches multiple documents, return answer from the most relevant single document only — never blend. If no document matches, return the refusal template verbatim. If no section number is available, cite the document name only.
