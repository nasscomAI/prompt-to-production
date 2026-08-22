skills:
  - name: identify_source_document
    description: Determine which single policy document can answer the question and return the document and relevant section.
    input: question string, indexed documents
    output: document name, section content
    error_handling: Return null/None if the question spans multiple documents or is entirely out of scope.

  - name: answer_from_document
    description: Answer only from the selected document and section, preserving all conditions and including citations.
    input: question, isolated document section
    output: answer string with citation
    error_handling: Fallback to the strict refusal template if the isolated section lacks the answer.

  - name: validate_policy_answer
    description: Verify that the generated answer is supported by the selected source, contains citations, and preserves mandatory conditions.
    input: generated answer, original section
    output: validated answer
    error_handling: Reject and replace with refusal template if unsupported claims, hedging, or condition-dropping are detected.
