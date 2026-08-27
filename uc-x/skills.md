skills:
  - name: retrieve_documents
    description: Loads all three policy files and indexes each numbered section by document.
    input: "list of file paths for policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt"
    output: "dict[document_name] -> list[{section:string, text:string}]"
    error_handling: "Raises clear error if any file is missing or has no parseable numbered sections."

  - name: answer_question
    description: Answers a policy question from one document section with citation, or returns exact refusal template.
    input: "question:string and indexed documents dict"
    output: "answer:string with citation '(source: <document> <section>)' or refusal template"
    error_handling: "Refuses if coverage missing, ambiguous, or requires cross-document blending; never hedges."
