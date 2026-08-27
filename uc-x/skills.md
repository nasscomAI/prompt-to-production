# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number for precise retrieval.
    input: List of file paths pointing to the policy documents.
    output: A structured dictionary mapping document names and section numbers to their specific text blocks.
    error_handling: Raises an exception if any of the specified policy documents cannot be found or read.

  - name: answer_question
    description: Searches the indexed documents to return a single-source answer with a citation, or outputs the strict refusal template.
    input: The indexed document dictionary and the user's question string.
    output: A string containing the exact answer with citation, or the verbatim refusal template.
    error_handling: If an answer requires blending across documents or isn't explicitly found, immediately returns the refusal template without attempting to guess.
