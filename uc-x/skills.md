# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_documents
    description: Load and index all available policy documents.
    input: Policy document text files.
    output: Indexed document sections.
    error_handling: Raise an error if any document cannot be loaded.

  - name: answer_question
    description: Search the indexed documents and answer from one source only.
    input: User question.
    output: Single-source answer with document and section citation.
    error_handling: Return the refusal template if the answer is unavailable.
