skills:
  - name: retrieve_documents
    description: Loads all three policy files and indexes them by document name and section number.
    input: policy_dir (path to the directory containing the three policy .txt files; defaults to ../data/policy-documents).
    output: A dict {document_name: {section_id: body_text}} with sections extracted from numbered X.Y clauses, continuation lines joined and whitespace normalised.
    error_handling: Any missing policy file prints an error to stderr and exits with status 1.

  - name: answer_question
    description: Searches the indexed documents and returns a single-source answer with citation, or the refusal template.
    input: question (string) and index (dict from retrieve_documents).
    output: A multi-line answer string "Answer: ..." followed by "Source: <document>, section <X.Y>" and the quoted clause text; or the verbatim refusal template when the question is not covered or the best matches span two documents.
    error_handling: No keyword match returns the refusal template exactly. Strong matches in two different documents return the refusal template (no blending). Ambiguous or empty questions are refused with the template rather than guessed.