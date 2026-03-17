# skills.md

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files, indexes by document name and section number
    input: List of document paths (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt)
    output: Indexed document content and sections
    error_handling: Return an error if any of the files are missing or cannot be read.

  - name: answer_question
    description: Searches indexed documents, returns single-source answer + citation OR refusal template
    input: User question and search results from indexed documents
    output: Single-source answer with source document name and section number, OR refusal template string
    error_handling: Return the exact refusal template if the answer is not in the documents or requires combining claims from two different documents.
