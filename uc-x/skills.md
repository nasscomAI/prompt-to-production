# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files, indexes by document name and section number.
    input: None
    output: A dictionary of indexed documents.
    error_handling: If a file is not found, it will raise an error.

  - name: answer_question
    description: Searches indexed documents, returns single-source answer + citation OR refusal template.
    input: A string containing the user's question.
    output: A string containing the answer and citation, or the refusal template.
    error_handling: If the question is ambiguous, it will ask for clarification.
