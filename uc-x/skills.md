skills:
  - name: retrieve_documents
    description: Loads and indexes the HR, IT, and Finance policy text files to enable precise searching by document name and section number.
    input:
      type: list
      format: File paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt.
    output:
      type: object
      format: Indexed data structure mapping section numbers and document names to raw text content.
    error_handling: Raises a file-not-found error if any of the three required policy documents are missing or inaccessible.

  - name: answer_question
    description: Analyzes indexed policy documents to provide a single-source answer with citations or triggers a strict refusal if the query is out-of-scope.
    input:
      type: string
      format: Natural language user question regarding company policies.
    output:
      type: string
      format: A factual answer citing [Document Name] [Section Number] OR the verbatim refusal template.
  error_handling: If the query matches a failure mode (e.g., cross-document blending or ambiguous coverage), the skill must output the exact refusal template without hedging or combining multiple sources.
