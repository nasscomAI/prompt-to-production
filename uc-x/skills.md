# skills.md — UC-X Skills Definition

skills:
  - name: retrieve_documents
    description: Reads and indexes policy documents (HR, IT, Finance) by document name, section number, and clause content.
    input: Directory path containing policy text files (e.g. data/policy-documents).
    output: Indexed dictionary of document sections and clauses.
    error_handling: Handles missing policy files gracefully by raising FileNotFoundError.

  - name: answer_question
    description: Searches indexed policy sections, performs single-source matching, appends source citations, or returns the exact refusal template.
    input: String question and indexed policy documents dictionary.
    output: String response containing single-source citation or exact verbatim refusal template.
    error_handling: Returns exact refusal template if question is unmentioned or if multi-document ambiguity exists.

