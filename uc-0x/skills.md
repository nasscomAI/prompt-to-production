# skills.md

skills:
  - name: retrieve_documents
    description: Loads and indexes all policy files from ../data/policy-documents/ by document name and section number.
    input: File paths to policy documents.
    output: Indexed collection of document sections.
    error_handling: Reports if files are missing; continues with available documents.

  - name: answer_question
    description: Searches indexed documents for a single-source answer. Returns the answer with citation or the mandatory refusal template.
    input: User question (string) and indexed documents.
    output: Single-source answer + citation OR verbatim refusal template.
    error_handling: Refuses to blend information from multiple sources. Uses exact refusal wording for unknown queries.
