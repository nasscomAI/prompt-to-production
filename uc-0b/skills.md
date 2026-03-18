# skills.md
# UC-X skills definition for policy-based question answering

skills:
  - name: retrieve_documents
    description: Load and index all policy documents by name and section for fast lookup.
    input: List of document file paths (string array)
    output: Indexed document object with sections, content, and document names
    error_handling: If a file is missing or unreadable, log the error and skip it; if all fail, raise a clear load error

  - name: answer_question
    description: Search indexed policy documents and return a single-source answer with citation, or refusal.
    input: User question (string)
    output: Answer text (string) — either a factual answer citing document + section, or the refusal template
    error_handling: If question matches multiple sources creating ambiguity, return refusal template; if question not found, return refusal template