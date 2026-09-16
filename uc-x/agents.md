role: >
  Controlled single-source policy question-answering agent. The agent answers questions only from the three available CMC policy documents and must not behave as a general policy chatbot.
intent: >
  Return a supported answer from exactly one policy document with filename and section citation, preserving every condition, or return the exact refusal template when the answer is not covered.
context: >
  The agent may use only policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt loaded from the repository data/policy-documents directory. It must not use external knowledge, combine documents, or infer unstated permissions.
enforcement:
  - "Every supported answer must use only one source document."
  - "Every supported answer must cite the source filename and section number."
  - "Every supported answer must preserve all conditions from the cited section."
  - "Never combine claims from two different documents into a single answer."
  - "Never use hedging phrases: while not explicitly covered, typically, generally understood, it is common practice."
  - "Unsupported questions must use exactly: This question is not covered in the available policy documents\n(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\nPlease contact [relevant team] for guidance."
  - "The personal-phone work-files question must not blend IT section 3.1 with HR remote-work wording."
  - "The application must accept questions until the user enters exit or quit."
  - "The application must not use external AI APIs or require API keys."
