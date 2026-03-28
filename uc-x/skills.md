# skills.md

skills:
  - name: retrieve_documents
    description: Loads and indexes the three mandatory policy documents (HR, IT, Finance) by document name and section number.
    input: None (uses predefined paths to `policy_hr_leave.txt`, `policy_it_acceptable_use.txt`, and `policy_finance_reimbursement.txt`).
    output: A collection of document objects containing section-level text and metadata.
    error_handling: Report if any of the three mandatory files are missing.

  - name: answer_question
    description: Analyzes the user's question, searches the indexed documents, and returns a cited single-source answer or the refusal template.
    input: User's question as a string.
    output: A response string containing the answer with citation (or refusal), as per the agent's enforcement rules.
    error_handling: Return the system refusal template if the answer cannot be found in a single source.
