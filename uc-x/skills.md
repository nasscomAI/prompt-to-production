# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and returns them as a single context string indexed by document name and section number.
    input: None.
    output: A string containing the full text of all 3 policies.
    error_handling: Raises an error if documents are missing or cannot be read.

  - name: answer_question
    description: Searches indexed documents and returns a single-source answer with citation OR the refusal template.
    input: The user's question (string) and the retrieved policy text (string).
    output: A string containing the answer with citation, or the exact refusal template.
    error_handling: Returns the exact refusal template if there is any ambiguity, if the answer is not found, or if it requires cross-document blending.
