# skills.md

skills:
  - name: retrieve_documents
    description: Loads the HR, IT, and Finance policy files and segments them into a multi-document index by section number.
    input: None (loads from specified paths in data/policy-documents/).
    output: A nested dictionary structure grouped by document and section.
    error_handling: System refusal if any of the three core documents are inaccessible.

  - name: answer_question
    description: Matches a user query against the policy index, applying zero-blending and refusal logic.
    input: User query string.
    output: A single-source response with citations OR the exact refusal template.
    error_handling: Triggers refusal template if query cannot be answered using only one section's logic.
