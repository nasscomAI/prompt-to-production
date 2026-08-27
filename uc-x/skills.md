# skills.md — UC-X Skills

skills:
  - name: retrieve_documents
    description: Loads and indexes all three policy files by filename and section headers.
    input: File paths to HR, IT, and Finance TXT files.
    output: Indexed dictionary of policy text.
    error_handling: Refuses to start if any of the three core files are missing.

  - name: answer_question
    description: Searches the index for the specific query and applies the RICE refusal logic.
    input: User question (String).
    output: Cited answer or the exact refusal template.
    error_handling: If multiple documents contain the same keywords, it selects the most relevant one without blending.