# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_documents
    description: Loads all three policy files and indexes them by document name and section number.
    input: List of policy file paths; list of strings.
    output: Indexed documents with section numbers and text.
    error_handling: Returns error if any file is missing, unreadable, or format invalid.

  - name: answer_question
    description: Searches indexed documents, returns single-source answer with citation or refusal template if not found.
    input: Indexed documents, question string.
    output: Answer text with document name and section citation, or refusal template verbatim.
    error_handling: Refuses and uses template if question not covered; returns error if input is incomplete or ambiguous; never blends cross-document claims.
