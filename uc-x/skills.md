# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads and indexes the three policy files by name and section number.
    input: Paths to three policy .txt files.
    output: Indexed searchable data repository.
    error_handling: Alert if core documents are unreadable.

  - name: answer_question
    description: Searches indexed docs to return a single-source answer with citation or refusal.
    input: String question.
    output: String answer with citation OR standard refusal.
    error_handling: Strict format control for refusal messages.

