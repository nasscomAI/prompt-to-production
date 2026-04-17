# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_documents
    description: Loads and indexes all policy files by document name and section number.
    input: file_paths (list)
    output: A dictionary of sections grouped by document.
    error_handling: If a file is missing, log the error and proceed with available files.

  - name: answer_question
    description: Searches indexed documents and returns a single-source answer with citation or the refusal template.
    input: question (string), indexed_docs (dict)
    output: A string containing the answer or refusal.
    error_handling: If ambiguity is found across multiple documents, default to the refusal template.
