skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them strictly by document name and section number.
    input: File paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt (List of Strings)
    output: Indexed text separated strictly by explicitly defined document names and section numbers (JSON/Dict)
    error_handling: Return a clear error if any of the three files are missing or cannot be read.

  - name: answer_question
    description: Searches indexed documents and returns a clean, single-source answer with a strict citation OR the exact refusal template.
    input: Search query/question and the indexed documents (String, JSON/Dict)
    output: A single-source answer with exact source citation (document name + section) OR the exact refusal template string. NEVER a blended result. (String)
    error_handling: Refuse to compute and output the refusal template exactly if the answer requires cross-document blending, inference, or is otherwise absent.
