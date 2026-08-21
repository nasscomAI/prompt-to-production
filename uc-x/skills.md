# skills.md — UC-X Policy Knowledge Assistant

skills:
  - name: retrieve_documents
    description: Loads and indexes all three municipal policy files by document name and section number.
    input: List of paths to the policy documents (HR, IT, Finance).
    output: A searchable index or structured representation of all policy clauses across the three files.
    error_handling: If any document is missing or unreadable, log the failure and notify the user about the incomplete index.

  - name: answer_question
    description: Retrieves a single-source answer for a user query from the policy index, or provides a refusal if out-of-scope.
    input: A string containing the user's question.
    output: A string containing the answer with document/section citations, or the exact refusal template.
    error_handling: If the query is ambiguous or spans multiple conflicting sources, prioritize the IT policy or use the refusal template to avoid blending.
