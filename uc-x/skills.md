# skills.md

skills:

- name: retrieve_documents
  description: Loads all 3 policy files and indexes them by document name and section number.
  input: A dictionary mapping document filenames to their file paths.
  output: A nested dictionary indexed by document name, then by section number (e.g., "3.1"), with text content as values.
  error_handling: Raise FileNotFoundError if any policy file is missing or unreadable.

- name: answer_question
  description: Searches indexed documents for a single-source answer, returns the answer with citation or the exact refusal template.
  input: A question string and the indexed documents dictionary.
  output: A single string — either a citation-backed answer from one document or the exact refusal template.
  error_handling: If relevant sections appear in more than one document, return the refusal template to prevent cross-document blending.
