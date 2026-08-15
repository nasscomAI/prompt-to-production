# skills.md

skills:
  - name: retrieve_documents
    description: Loads the three policy files and indexes their content by document name and section number.
    input: File paths to the three policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
    output: An index mapping document name -> section number -> section content, ready for lookup.
    error_handling: If a file is missing or unreadable, reports the missing file and refuses to answer rather than continuing with partial data.

  - name: answer_question
    description: Searches the indexed documents and returns a single-source answer with citation, or the verbatim refusal template.
    input: A user question (string) and the index produced by retrieve_documents.
    output: Either a single-source answer citing document name + section number, or the exact refusal template.
    error_handling: Returns the refusal template verbatim when the question is not covered by any document, or when the answer would require blending claims from two documents.
