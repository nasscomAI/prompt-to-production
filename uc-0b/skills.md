# skills.md

skills:
  - name: retrieve_policy
    description: Loads a policy text file and returns its content as structured numbered sections.
    input: >
      A filesystem path (string) to a .txt policy document, passed via the
      --input CLI argument (e.g. ../data/policy-documents/policy_hr_leave.txt).
    output: >
      A dictionary (or equivalent structured object) mapping clause numbers
      (e.g. "2.3", "5.2", "7.2") to the exact clause text, plus a header
      field containing the document title. Numbering keys must match the
      source document exactly — no renumbering, no merging of adjacent
      clauses.
    error_handling: >
      If the file does not exist, is unreadable, or is empty, raise a
      FileNotFoundError / ValueError with a clear message and stop. If the
      document contains no recognisable numbered clause headings (e.g. lines
      matching the pattern "<number>.<number> ..."), refuse to proceed and
      report that the document does not match the expected policy schema
      rather than attempting to guess clause boundaries.

  - name: summarize_policy
    description: Takes the structured clause map produced by retrieve_policy and produces a compliant summary with clause references.
    input: >
      The structured clause map returned by retrieve_policy (clause number
      -> clause text), plus the clause inventory defined in README.md
      which acts as the ground-truth checklist of the 10 clauses that must
      appear.
    output: >
      A plain-text summary written to the path given by --output
      (e.g. summary_hr_leave.txt). Each of the 10 ground-truth clauses
      (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) appears as its own
      bullet or line, prefixed with the clause number, with every condition
      preserved verbatim. Clauses that cannot be safely summarised are
      quoted verbatim and flagged with [VERBATIM — see clause X.Y].
    error_handling: >
      For each clause in the ground-truth inventory, verify it is present in
      the clause map; if missing, append a flagged note rather than invent
      content. For each clause, verify that every named condition
      (approver, threshold, timeframe, exception, absolute prohibition) is
      present in the produced bullet; if any condition would be dropped,
      quote the clause verbatim and flag it instead of paraphrasing. If the
      final summary contains any forbidden scope-bleed phrase
      ("generally", "typically", "as is standard practice",
      "employees are usually expected to", "it is advisable"), the
      skill must reject its own output and regenerate that bullet before
      returning.