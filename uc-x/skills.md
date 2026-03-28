# skills.md

skills:
  - name: retrieve_documents
    description: Opens all 3 policy txt files and indexes them strictly by document name and section number without semantic loss.
    input: directories containing policy txt files.
    output: structured dictionary containing the full text segmented by Section/Clause ID.
    error_handling: Return fatal error if document is missing.

  - name: answer_question
    description: Executes keyword and regex searches against the indexed documents based on strict zero-hallucination queries.
    input: User string question, retrieved document payload.
    output: Exact citation string (Doc + Section) or the verbatim refusal template.
    error_handling: Trigger refusal template string exactly on any ambiguity or if multiple documents are triggered simultaneously preventing cross-doc blending.
