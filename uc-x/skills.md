# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.
skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes their content by document name and section number.
    input: none (reads from fixed paths in ../data/policy-documents/).
    output: A dict keyed by document name, each containing a dict of {section_number: section_text}.
    error_handling: If any of the 3 files is missing, raise a clear error naming which file is missing rather than proceeding with partial documents silently.

  - name: answer_question
    description: Searches indexed documents for the single best-matching section and returns either a cited single-source answer or the exact refusal template.
    input: question (str), indexed_documents (from retrieve_documents).
    output: A string — either "[answer] (Source: document_name, section X.X)" or the exact refusal template.
    error_handling: If the question's best match spans two documents, do not blend — either answer from the single most relevant section or use the refusal template.