skills:
  - name: retrieve_documents
    description: Loads policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt, parsing them into structured sections indexed by document name and section number.
    input: docs_dir (str) - path to directory containing policy text files
    output: dict of indexed documents with sections and clause texts
    error_handling: Raises FileNotFoundError if any policy file is missing.

  - name: answer_question
    description: Evaluates a user question against single policy document sections, returning a single-source cited answer [Document Name, Section X.Y] or the exact refusal template if ungrounded.
    input: question (str), indexed_docs (dict)
    output: answer string containing single-source text + citation OR exact refusal template
    error_handling: Strictly output verbatim refusal template if question cannot be answered from a single source without hedging or cross-document blending.

