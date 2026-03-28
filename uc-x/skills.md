# skills.md — UC-X Ask My Documents Assistant

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files (`policy_hr_leave.txt`, `policy_it_acceptable_use.txt`, `policy_finance_reimbursement.txt`), parsing and indexing them by document name and section number.
    input: None or optional directory path mapping to the policy documents.
    output: A structured index (dictionary or object) mapping document names and section numbered headers to their specific textual content.
    error_handling: Systematically crash or log if a policy document is missing, ensuring that the assistant does not operate on an incomplete document set.

  - name: answer_question
    description: Searches the indexed documents for an exact answer to the user's question, returning a single-source answer with citation, or safely falling back to the refusal template.
    input: The indexed documents dictionary and the user's question string.
    output: A string containing the exact answer with `[Document Name - Section X.X]` citation, OR the exact refusal template.
    error_handling: If matches are found across multiple differing documents that conflict or blend context, abort the blend and return the refusal template.
