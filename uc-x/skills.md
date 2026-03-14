# skills.md

skills:
  - name: retrieve_documents
    description: Loads all policy files and indexes them by document name and section number.
    input: File paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt.
    output: A searchable index or collection of structured text documents broken down by section numbers and specific clauses.
    error_handling: Raise an error if any of the required policy files are missing or unreadable.

  - name: answer_question
    description: Searches the indexed documents to return a strict, single-source answer with a citation, or outputs the strict refusal template.
    input: A user question string and the searchable policy document index.
    output: A text answer citing one single document and section, OR the exact refusal template if the answer cannot be sourced cleanly.
    error_handling: If an answer requires cross-document blending or the information is not present, immediately output the verbatim refusal template.
