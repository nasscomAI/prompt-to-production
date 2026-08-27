# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_documents
    description: loads all 3 policy files, indexes by document name and section number
    input: Search query or keywords
    output: Relevant sections from the policy documents
    error_handling: Return empty results if no match is found

  - name: answer_question
    description: searches indexed documents, returns single-source answer + citation OR refusal template
    input: Question string
    output: Single-source answer with citation, or the exact refusal template
    error_handling: If information spans multiple documents or is ambiguous, use the exact refusal template
