skills:
  - name: [retrieve_documents]
    description: [ Load all three supplied policy documents and index their contents by
      document name and numbered section so that answers can be traced to
      their original source.]
    input: [policy_hr_leave.txt, policy_it_acceptable_use.txt, and
      policy_finance_reimbursement.txt.]
    output: [An indexed collection of policy sections identified by source document
      name and section number.]
    error_handling: [ If a required policy document cannot be loaded, report the missing
      document and do not invent or substitute policy content.]

  - name: [answer_question]
    description: [Search the indexed policy documents for the user's question and return
      an answer supported by one source document and its section citation,
      or return the exact refusal template when the question is not covered.]
    input: [A user policy question and the indexed contents of the three policy
      documents.]
    output: [A factual answer based on a single source document with document name
      and section number, or the exact required refusal template.]
    error_handling: [Never combine claims from multiple documents, never guess missing
      information, and never use hedged language when the answer is not
      supported by the documents.]
