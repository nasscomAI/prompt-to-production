# skills.md

skills:
  - name: retrieve_documents
    description: Load all 3 policy files and index them by document name and section number.
    input: list of file_paths (the 3 .txt policy files).
    output: dict {doc_name: {section_number: text}} — same numbered-clause parsing as UC-0B, per document.
    error_handling: If a file is missing/unreadable, raise immediately naming the missing file — never silently proceed with only 2 of 3 documents.

  - name: answer_question
    description: Score every section across all 3 documents against the question, pick the single best-matching document, and return either a cited single-source answer or the exact refusal template.
    input: question (str), index (dict from retrieve_documents).
    output: str — either "[Source: <doc>, Section <N>] <verbatim clause text>" or the exact refusal template.
    error_handling: If the top-scoring section's document is tied (within margin) with a section from a DIFFERENT document, refuse rather than guess which one — this is the cross-document-ambiguity case, not a bug to silently resolve.
