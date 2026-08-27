# skills.md

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes their content by document name and section number.
    input: none (reads the 3 fixed paths under ../data/policy-documents/).
    output: dict keyed by document name, each value a list of {section_id, text} entries.
    error_handling: If any of the 3 files is missing, raise a clear error naming the missing file — do not start the CLI with partial document coverage.

  - name: answer_question
    description: Searches indexed documents for a single-source answer to the user's question, or returns the refusal template.
    input: `question` (string) and the indexed documents dict from retrieve_documents.
    output: either {answer, source_document, section_id} for a single-source match, or the exact refusal template string when no document covers the question.
    error_handling: If the question matches sections in more than one document with no way to answer from one alone, do not blend — return the refusal template rather than a combined answer.
