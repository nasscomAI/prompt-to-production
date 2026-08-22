# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.
skills:
  - name: retrieve_documents
    description: Loads all three policy files and indexes content by document name and section number.
    input: Paths to the three policy .txt files (strings).
    output: Structured index of clauses with document name, section number, and text.
    error_handling: If any file is missing or unreadable, return "INVALID_INPUT" and skip indexing for that file.

  - name: answer_question
    description: Searches indexed documents for a question, returns single-source answer with citation or refusal template.
    input: User question (string).
    output: Answer text with citation OR refusal template verbatim.
    error_handling: If no relevant clause is found, return the refusal template exactly. If multiple documents match but create ambiguity, refuse and return the template instead of blending.

