skills:
  - name: retrieve_documents
    description: >
      Loads all three policy files and indexes their clauses by document name and
      section number.
    input: >
      doc_dir (str) — directory containing policy_hr_leave.txt,
      policy_it_acceptable_use.txt and policy_finance_reimbursement.txt.
    output: >
      list of dicts, each with doc (str, the filename), section (str, e.g.
      "3.1"), heading (str, the enclosing section title) and text (str, the
      clause with wrapped lines rejoined and nothing else altered).
    error_handling: >
      Exits naming any of the three expected files that is missing or unreadable,
      before any question is answered, rather than answering from a partial
      corpus — an index silently missing the IT policy would refuse IT questions
      as uncovered rather than reporting that it could not read them. A file
      yielding no clauses is reported by name for the same reason.

  - name: answer_question
    description: >
      Answers one question from exactly one document with a citation, or returns
      the refusal template verbatim.
    input: >
      question (str); index (list of dicts from retrieve_documents).
    output: >
      dict with answer (str), doc (str or None), sections (list of str) and
      refused (bool). A non-refused answer quotes only clauses from the single
      document named in doc, and its rendered text carries that filename and
      those section numbers.
    error_handling: >
      Returns the refusal template unchanged when no clause scores 2 or above,
      and equally when the best-scoring document leads the second by less than 1, because answering from either would be a silent
      choice between sources. An empty or whitespace-only question is refused the
      same way. It never emits a hedging phrase and never merges text from two
      documents, and the rendered answer is checked for both before it is
      returned.
