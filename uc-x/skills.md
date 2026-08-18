# skills.md

skills:
  - name: retrieve_documents
    description: Loads all policy text files and indexes them by document name and section number.
    input: Paths to the three policy text files.
    output: A structured index of document sections and content.
    error_handling: If a file is missing or cannot be read, raise FileNotFoundError.

  - name: answer_question
    description: Finds the best single-document answer for a policy question and returns it with citation or the exact refusal template.
    input: A question string and the structured document index.
    output: Either a quoted answer with document and section citation or the refusal template.
    error_handling: If no single-document answer exists, return the exact refusal template; if the question is ambiguous, refuse rather than guess.
