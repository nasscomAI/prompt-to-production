# skills.md

skills:
  - name: retrieve_documents
    description: >
      Loads the three policy files and indexes them by document name and
      section number.
    input: Paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, and
      policy_finance_reimbursement.txt.
    output: A dict mapping document filename -> {section_number: section_text},
      where section numbers are numbered clauses such as 2.6, 3.1, 5.2.
    error_handling: If any document cannot be read or contains no numbered
      sections, raise an error and refuse to answer rather than answering from
      a partial index.

  - name: answer_question
    description: >
      Searches the indexed documents and returns either a single-source answer
      with citation or the exact refusal template.
    input: A question string and the index from retrieve_documents.
    output: A single-source answer citing document name and section number, or
      the exact refusal template when the question is not covered.
    error_handling: Resolve to exactly one document — if the question maps to
      sections from two different documents, prefer the most specific single
      match; if genuine ambiguity remains, refuse using the template rather
      than blending. Apply the refusal template verbatim when no section
      matches.
