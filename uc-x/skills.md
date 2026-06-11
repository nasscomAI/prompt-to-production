skills:
  - name: retrieve_documents
    description: Load all three policy files and index their contents by document name and section number.
    input: File paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt.
    output: Indexed document collection mapping each document name to a list of sections, where each section has a section number and its full text.
    error_handling: If a file is missing or unreadable, skip it with a warning and continue loading the remaining files.

  - name: answer_question
    description: Search the indexed documents for the most relevant section and return a single-source answer with citation, or the exact refusal template.
    input: User question string and the indexed document collection.
    output: Either a formatted answer citing the source document name and section number, or the exact refusal template.
    error_handling: If the answer requires combining information from multiple documents, return the refusal template. If no section meets the relevance threshold, return the refusal template. Never hedge or speculate.