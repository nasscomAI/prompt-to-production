# skills.md

skills:
  - name: retrieve_documents
    description: loads all 3 policy files, indexes by document name and section number
    input: File paths to the three policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
    output: Indexed document store — a mapping of document names to their sections with section numbers, titles, and content.
    error_handling: If a file is missing or unreadable, log the error and exclude that document from the index. Do not hallucinate missing content.

  - name: answer_question
    description: searches indexed documents, returns single-source answer + citation OR refusal template
    input: A natural-language employee question as a string.
    output: Either a factual answer string containing the source document name and section number, or the refusal template verbatim.
    error_handling: If no document contains a relevant answer, return the refusal template. If multiple documents seem relevant, still answer from only one — never blend. If a document's section is ambiguous, return the refusal template rather than guess.
