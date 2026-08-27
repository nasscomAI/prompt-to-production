# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_documents
    description: Loads and indexes all policy documents by section and keyword for retrieval.
    input: Directory path containing policy text files.
    output: Dictionary mapping section IDs to text content.
    error_handling: Fail if any of the three mandatory policy files are missing.

  - name: answer_question
    description: Finds relevant sections and generates a citation-backed answer without blending sources.
    input: User question string.
    output: Answer string with [Source Section] or the refusal template.
    error_handling: Return refusal template if match confidence is low or if blending is required.
