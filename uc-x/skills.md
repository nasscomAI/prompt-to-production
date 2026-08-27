skills:
  - name: retrieve_documents
    description: Loads the three policy text files and indexes them as ordered clauses grouped by document name and section number.
    input:
      type: list[file]
      format: >
        Three plain-text policy document paths:
        `policy_hr_leave.txt`, `policy_it_acceptable_use.txt`, and
        `policy_finance_reimbursement.txt`.
    output:
      type: object
      format: >
        Indexed document store containing document names, section headings, and
        clause records with `section_number`, `section_heading`, and `text`.
    error_handling: >
      If any required file is missing, unreadable, or cannot be parsed into
      numbered sections, abort with a clear error rather than answering from a
      partial index. Preserve source wording exactly; never infer missing
      sections from context or formatting.

  - name: answer_question
    description: Searches the indexed clauses and returns either a single-source cited answer or the exact refusal template.
    input:
      type: object
      format: >
        Indexed documents plus a free-text user question string.
    output:
      type: object
      format: >
        Either `answer` containing a single-source response with document name
        and section citation, or `answer` containing the exact refusal template.
    error_handling: >
      If the question is not covered, matches multiple documents without a clear
      single-source answer, or would require combining claims from different
      policies, return the refusal template exactly. Never hedge, never invent
      policy text, and never answer without naming the source document and
      section number for supported claims.
