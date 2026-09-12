# skills.md

skills:
  - name: retrieve_documents
    description: >
      Loads all three CMC policy files, indexes every numbered section by
      document name and section number, and preserves original document
      boundaries and section numbers exactly as they appear in the source.
    input: >
      None (fixed file set):
      ../data/policy-documents/policy_hr_leave.txt,
      ../data/policy-documents/policy_it_acceptable_use.txt,
      ../data/policy-documents/policy_finance_reimbursement.txt.
    output: >
      An index mapping each document name to its numbered sections
      (e.g. 2.6, 3.1, 5.2) with the verbatim text of each section preserved.
    error_handling: >
      If a policy file is missing or unreadable, stop and raise a clear error.
      Never proceed with a partial or guessed document set.

  - name: answer_question
    description: >
      Searches the indexed documents, returns a single-source answer with the
      document filename and section number citation, preserves every relevant
      condition and prohibition, or returns the exact refusal template when
      the question is not covered.
    input: >
      A free-text question string from the user.
    output: >
      Either (a) an answer grounded in ONE source document, citing the
      document filename and section number(s) (e.g. policy_hr_leave.txt,
      Section 2.6), quoting the section text verbatim; or (b) the exact
      refusal template when the question is unsupported.
    error_handling: >
      Refuses with the exact refusal template when no single document clearly
      covers the question, when the best match is below a confidence
      threshold, or when a correct answer would require blending claims from
      different documents. Never blends claims from different documents and
      never uses outside knowledge.