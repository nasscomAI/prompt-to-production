# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number for fast lookup.
    input: base_path (string — path to the policy-documents directory containing the 3 .txt files).
    output: A document index — dict keyed by document filename, each containing a list of section objects with section_number and text. Enables lookup by document + section.
    error_handling: If any of the 3 expected files is missing, print a warning but continue with available files. If no files found, exit with error.

  - name: answer_question
    description: Searches the indexed documents for relevant content, returns a single-source answer with citation OR the refusal template.
    input: question (string — the user's natural language question), doc_index (the index from retrieve_documents).
    output: Either a factual answer string with [Document: section X.Y] citation from a single source document, OR the exact refusal template if the question is not covered.
    error_handling: If the question matches content in multiple documents, answer from the most specific/relevant single document only — never blend. If genuinely ambiguous across documents, use the refusal template rather than risk blending.
