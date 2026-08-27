# skills.md

skills:

- name: retrieve_documents
  description: Loads and indexes the three policy documents by document name and section numbers for efficient searching.
  input: List of file paths to the policy documents.
  output: A dictionary indexed by document name, containing sections keyed by section numbers.
  error_handling: If a file cannot be loaded, skip it and continue with available documents; report missing files.

- name: answer_question
  description: Searches the indexed documents for relevant information and returns a single-source answer with citation or the refusal template.
  input: Question string and the indexed documents dictionary.
  output: Either an answer string with citation or the exact refusal template.
  error_handling: If no relevant information found, return the refusal template; if multiple documents match, refuse to avoid blending.
