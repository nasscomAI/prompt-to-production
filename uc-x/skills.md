# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_documents
    description: Loads all policy text files and indexes them by document name and section number for precise retrieval.
    input: List of paths to policy .txt files.
    output: A structured index of policy content.
    error_handling: Fail if any specified file is missing or unreadable.

  - name: answer_question
    description: Searches the indexed policies to provide a single-source answer with citations or the mandatory refusal template.
    input: User question string and indexed policy content.
    output: Answer string with document and section citations OR the refusal template.
    error_handling: If multiple documents conflict or provide ambiguous answers, refuse to blend and provide the best single-source answer or the refusal template.
