# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number.
    input: paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt under ../data/policy-documents.
    output: index of sections {doc, id, title, body} with wrapped lines joined; used for scoring and citation.
    error_handling: missing/unreadable policy file → ERROR line + exit code 1 (never answers from a partial corpus); zero indexed sections → ERROR line + exit code 1.

  - name: answer_question
    description: Searches the indexed documents and returns a single-source cited answer OR the refusal template.
    input: natural-language question string.
    output: answer text starting with "[policy_<name>.txt §N.N]" quoting only sentences from that one section, or the verbatim refusal template with the contact team routed by topic (HR/IT/Finance).
    error_handling: fewer than two distinctive term matches → refusal template (never guesses); any answer that would contain a hedging phrase is discarded and replaced by the refusal template; empty input re-prompts without crashing.
