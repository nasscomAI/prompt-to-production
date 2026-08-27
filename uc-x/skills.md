# skills.md — UC-X

skills:
  - name: retrieve_documents
    description: >
      Loads all three CMC policy documents and builds an index keyed by
      (document_name, section_number, clause_number). Preserves the exact
      text of each clause. Also records which topic each document owns.
    input: >
      A dict {document_name: path} for the three policy files
      (policy_hr_leave.txt, policy_it_acceptable_use.txt,
      policy_finance_reimbursement.txt).
    output: >
      A dict {
        "clauses": [{"doc": str, "section": str, "clause": str, "text": str}, ...],
        "doc_topics": {"policy_hr_leave.txt": ["leave", "sick", ...], ...}
      }.
    error_handling: >
      If any of the three files is missing or empty, exit non-zero with
      a clear message naming the file. Never silently proceed with a
      partial index.

  - name: answer_question
    description: >
      Answers a natural-language question by matching the question against
      the indexed clauses. Returns either a single-source cited answer OR
      the exact refusal template — never a blended answer, never a
      hedged answer.
    input: >
      question (str), index (dict from retrieve_documents).
    output: >
      dict {"answer": str, "source_doc": str | None, "sections": [str],
      "refused": bool}. If refused=True the answer is the verbatim refusal
      template. If refused=False the answer contains a citation of the
      form "(source: <doc>, section <n>)".
    error_handling: >
      If the top scoring clauses span more than one document, refuse.
      If no clause scores above the confidence threshold, refuse.
      Never fill gaps with prior knowledge or paraphrased blends.
