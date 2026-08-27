skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them strictly by document name and section number.
    input: File paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt.
    output: A structured index mapping document name and section numbers to the exact verbatim text found.
    error_handling: Return an error if a policy document cannot be loaded or properly parsed into distinct numbered sections.

  - name: answer_question
    description: Searches the indexed documents to answer the user's question, strictly returning either a single-source answer with citation or the exact refusal template.
    input: The user's query (string) and the structured index of policy documents.
    output: A precise answer explicitly citing the source document name and section number, OR the exact refusal template string constraint.
    error_handling: Refuse to formulate answers requiring cross-document blending. Discard ambiguous matches. If no single explicit matching constraint is found, fall back entirely to the exact wording of the refusal template.
