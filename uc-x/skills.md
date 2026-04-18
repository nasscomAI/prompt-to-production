skills:
  - name: retrieve_documents
    description: Loads the three policy text files and indexes their content strictly by document name and numbered section.
    input: File paths for `policy_hr_leave.txt`, `policy_it_acceptable_use.txt`, and `policy_finance_reimbursement.txt`.
    output: A structured database or dictionary where every clause is strictly mapped to its source document and section number.
    error_handling: If a file is missing or unreadable, log the exact file name that failed and continue indexing the others.

  - name: answer_question
    description: Searches the indexed documents and returns a strict, single-source answer with a citation, or the exact refusal template.
    input: The indexed document dictionary and a user query string.
    output: A clear text answer that cites the source document and section, OR the exact verbatim refusal template.
    error_handling: If the answer requires blending concepts from multiple documents, or if no single section provides a complete answer, immediately output the refusal template instead of attempting to guess or hedge.
