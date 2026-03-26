# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files, indexes by document name and section number.
    input: None
    output: Documents indexed by name and section.
    error_handling: Log error if files are missing or unreadable.

  - name: answer_question
    description: Searches indexed documents, returns single-source answer + citation OR refusal template.
    input: User question (string).
    output: Policy-based answer with citation or refusal template (string).
    error_handling: Return refusal template if no relevant information is found.
