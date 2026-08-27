# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_documents
    description: loads all 3 policy files, indexes by document name and section number
    input: List of paths to the 3 policy files.
    output: Indexed dictionary mapping document names and sections to their text.
    error_handling: System exits if any of the files cannot be read.

  - name: answer_question
    description: searches indexed documents, returns single-source answer + citation OR refusal template
    input: String question, Indexed dictionary of documents.
    output: String representing the precise answer with citation or the exact refusal template.
    error_handling: Uses the exact refusal template if the answer is ambiguous, missing, or requires cross-document blending.
