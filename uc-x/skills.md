# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files, indexes by document name and section number.
    input: List of file paths to the policy documents.
    output: Indexed structure (e.g., dict of document -> sections -> text).
    error_handling: If a file cannot be loaded, report the error and skip that document.

  - name: answer_question
    description: Searches indexed documents, returns single-source answer + citation OR refusal template.
    input: Question string and indexed documents.
    output: Answer string with citation or refusal template.
    error_handling: If search fails or question spans multiple documents, use refusal template.
