# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: >
      Loads all three policy files and indexes their content by document
      name and section number.
    input: >
      none — paths are resolved relative to the repo data directory.
    output: >
      dict: {document_name: {section_no: clause_text}} for
      policy_hr_leave.txt, policy_it_acceptable_use.txt,
      policy_finance_reimbursement.txt.
    error_handling: >
      A missing or unreadable policy file reports an error and exits;
      non-clause lines (headers, box-drawing separators) are skipped.

  - name: answer_question
    description: >
      Searches the indexed documents and returns a single-source answer
      with citation, or the exact refusal template.
    input: >
      docs — indexed documents from retrieve_documents; question — str.
    output: >
      str — verbatim clause text plus "Source: <document>, section <X.Y>",
      or the exact refusal template when the question is not covered.
    error_handling: >
      No matching section, or the top two candidate sections come from
      different documents, or no distinctive topic phrase is found:
      returns the refusal template verbatim — never a blend, never a
      hedged answer.