skills:
  - name: retrieve_documents
    description: Loads all three policy files and indexes every clause by document name and section number.
    input: Folder path containing policy_hr_leave.txt, policy_it_acceptable_use.txt and policy_finance_reimbursement.txt.
    output: List of clause records with document name, section number, section title, clause text and search tokens.
    error_handling: Raises a clear error naming the file if any of the three documents is missing; ignores separator lines and blank lines; never invents clauses.

  - name: answer_question
    description: Searches the indexed clauses and returns a single-source answer with document and section citations, or the refusal template.
    input: Question string typed by the user, plus the clause index from retrieve_documents.
    output: Text with the source document name and the quoted clause(s) with section numbers, or the exact refusal template.
    error_handling: If the best match is too weak, or a different document scores almost as high (risk of blending), returns the refusal template; an empty question gets a prompt to type a question; never guesses.