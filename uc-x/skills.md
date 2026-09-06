skills:
  - name: retrieve_documents
    description: Loads the three approved policy files and indexes complete clauses by document filename and section number.
    input: "Directory containing the three required UTF-8 .txt policy files."
    output: "A validated document index mapping each approved filename to its ordered clause references and complete clause text."
    error_handling: "Stop with a clear error if a required file is missing or unreadable, contains no numbered clauses, repeats a clause reference, or has text that cannot be assigned safely. Never infer missing content."

  - name: answer_question
    description: Retrieves relevant clauses and returns a single-document answer with citations or the exact refusal template.
    input: "A non-empty natural-language question and the validated document index from retrieve_documents."
    output: "Complete source clauses from exactly one document, each labelled with filename and section number, or the exact refusal template."
    error_handling: "Refuse unsupported, ambiguous or cross-document questions. Never blend documents, broaden limited permission, hedge, omit clause conditions or answer without section-level citations."
