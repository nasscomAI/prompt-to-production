skills:
  - name: retrieve_documents
    description: Loads all 3 policy files (`policy_hr_leave.txt`, `policy_it_acceptable_use.txt`, `policy_finance_reimbursement.txt`), indexing them structurally by document name and section number.
    input: No input parameters required; execution triggers document loading on startup.
    output: A parsed document index where text clauses are securely mapped to their source document name and precise section number.
    error_handling: If a policy document cannot be successfully loaded or text cannot be mapped to a precise section, fail safely to prevent un-cited outputs.

  - name: answer_question
    description: Searches the indexed documents and returns either a direct single-source answer with its citation or the exact exact refusal template if merging is required.
    input: The specific employee policy question (string).
    output: A direct, single-source textual answer appended with its citation, OR exactly the fixed refusal template.
    error_handling: If the answer requires facts from multiple documents (e.g., HR + IT policies) or is not explicitly found, return the exact refusal template ("This question is not covered in the available policy documents...") without attempting to guess.
