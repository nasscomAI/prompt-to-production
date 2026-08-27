# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number.
    input: None (loads from data/policy-documents/).
    output: A structured index of policy content by document and section.
    error_handling: Reports missing files and exits if any of the three core documents are not found.

  - name: answer_question
    description: Searches the indexed documents and returns a single-source answer with citation or the exact refusal template.
    input: User question as a string.
    output: String containing the answer + citation OR the refusal template.
    error_handling: Returns the refusal template if the question is ambiguous or not directly answered by a single document.
