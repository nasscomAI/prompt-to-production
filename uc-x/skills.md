# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

    output: [What does it return? Type and format.]
  - name: retrieve_documents
    description: Loads and indexes policy documents by section number and text.
    input: Paths to the three policy text files.
    output: Document index keyed by filename and section number.
    error_handling: Raises clear errors when any required document is missing or unreadable.
    output: [Type and format]
  - name: answer_question
    description: Answers a policy question with a single-source citation or exact refusal template.
    input: User question text and retrieved document index.
    output: Answer string with citation, or refusal template when out of scope.
    error_handling: Returns refusal template if retrieval confidence is low or if answering would require cross-document blending.
