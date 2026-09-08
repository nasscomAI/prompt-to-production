skills:
  - name: retrieve_documents
    description: Ingests all three policy text documents, segments them into structured sections and numbered clauses, and builds an index mapped by document filename and section identifier.
    input: Directory path or explicit file paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt.
    output: Indexed corpus structure containing parsed sections, clauses, and document metadata.
    error_handling: Raises FileNotFoundError if any of the three required policy files cannot be read.

  - name: answer_question
    description: Processes a user query against the indexed documents, identifying the single most authoritative matching section, returning a single-source cited answer, or triggering the verbatim refusal template.
    input: User question string and indexed corpus.
    output: Text response containing single-source factual answer with [document § section] citation, OR the standardized refusal template.
    error_handling: Detects queries spanning conflicting documents and enforces single-document precedence or clean refusal. Rejects queries outside document scope using the exact refusal template.
