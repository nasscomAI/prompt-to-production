# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads the three CMC policy files from data/policy-documents/, parses them into sections and numbered clauses, and indexes each clause by document name and section number.
    input: none (uses fixed paths for policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt)
    output: list of clause dicts, each with doc (file name), section (clause id like "2.6"), and text (full clause verbatim)
    error_handling: Raises FileNotFoundError listing any missing policy file; skips separators and blank lines so clause text stays clean.

  - name: answer_question
    description: Routes a question to exactly one document, selects the best matching clause in it, and returns the full clause verbatim with its document name and section number — or the refusal template when the question is not covered.
    input: question (str), index (list of clause dicts from retrieve_documents)
    output: dict {doc, section, text} for a covered question, or the refusal template string verbatim
    error_handling: Refuses when no document matches the question; refuses when two documents match equally (blend guard — never mixes sources); never paraphrases, never uses hedging phrases, and always returns the complete clause text.
