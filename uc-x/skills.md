# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_documents
    description: loads the 3 policy files (HR, IT, Finance) and indexes them by document name and section number.
    input: File paths to policy documents.
    output: A structured collection of policy sections categorized by their source document.
    error_handling: Halt and report if any document is missing or unreadable.

  - name: answer_question
    description: searches the indexed documents for a single-source answer with a mandatory citation, or the exact refusal template.
    input: User natural language question.
    output: A response containing the specific policy clause and citation, or the verbatim refusal template.
    error_handling: Trigger the refusal template if multiple documents conflict or would require blending.