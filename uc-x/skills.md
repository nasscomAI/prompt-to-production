# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_documents
    description: Loads all three policy files and indexes them by document name and section number for searching.
    input: List of file paths to the policy documents (list of strings).
    output: Dictionary with document names as keys and content as values.
    error_handling: If a file cannot be loaded, reports the error and continues with available documents.

  - name: answer_question
    description: Searches the indexed documents for an answer, returns single-source answer with citation or the exact refusal template.
    input: Question string and documents dictionary.
    output: Answer string with citation or refusal template.
    error_handling: Never blends information from multiple documents; uses refusal template if question not covered.
