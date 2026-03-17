# skills.md — UC-0B Policy Summariser

skills:
  - name: retrieve_policy
    description: Loads a plain-text policy file and returns its content parsed into
      a list of numbered sections, each containing its heading and ordered clauses.
    input: A file path string pointing to a .txt policy document structured with
      numbered sections (e.g. "2. ANNUAL LEAVE") and numbered clauses (e.g. "2.3 ...").
    output: A list of section dicts, each with keys — section_number (str),
      heading (str), and clauses (list of dicts with keys clause_id and text).
    error_handling: If the file does not exist, raise FileNotFoundError with the
      path. If the file is empty or contains no recognisable numbered clauses,
      raise ValueError with a message describing what was found.

  - name: summarize_policy
    description: Takes the structured section list from retrieve_policy and produces
      a clause-complete, binding-verb-preserving summary written to an output file.
    input: A list of section dicts (as returned by retrieve_policy) and an output
      file path string where the summary will be written.
    output: A plain-text summary file where every clause is referenced by its
      clause ID, binding verbs are preserved verbatim, multi-condition obligations
      list all conditions, and any clause at risk of meaning loss is marked [VERBATIM].
    error_handling: If any section contains zero clauses after parsing, include a
      warning line in the output flagging the section as [EMPTY — VERIFY SOURCE].
      Never silently skip a section or clause.
