skills:
  - name: retrieve_policy
    description: Loads a .txt policy file from disk and returns its content parsed into structured, numbered sections keyed by clause number.
    input: >
      A file path string pointing to a plain-text policy document (e.g.
      ../data/policy-documents/policy_hr_leave.txt). The file must be UTF-8
      encoded and use numbered section headings (e.g. "2.3", "3.2").
    output: >
      A structured object (dict / dataclass) where each key is a clause
      identifier (string, e.g. "2.3") and each value is the full verbatim
      text of that clause as a string. Section hierarchy (chapter → clause)
      is preserved as nested keys where applicable.
    error_handling: >
      If the file path does not exist or cannot be read, raise FileNotFoundError
      with the attempted path. If the file is empty or contains no recognisable
      numbered sections, raise ValueError with message "No numbered clauses
      detected — verify input file format." Do not silently return an empty
      structure.

  - name: summarize_policy
    description: Takes the structured clause sections produced by retrieve_policy and produces a compliant summary that preserves every clause, all multi-condition obligations, and binding verbs, with inline clause references.
    input: >
      A structured clause object as returned by retrieve_policy (dict mapping
      clause ID strings to verbatim clause text strings).
    output: >
      A plain-text summary string in which each summarised clause is prefixed
      with its clause reference (e.g. "[2.3]"), binding verbs are retained
      verbatim, and any clause that could not be safely paraphrased is
      reproduced verbatim and tagged with [VERBATIM — summarisation would
      alter meaning].
    error_handling: >
      If the input structure is missing any of the 10 tracked clauses
      (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2), raise
      ValueError listing the missing clause IDs before proceeding. Never
      silently omit a clause from the output. If a clause text is present
      but ambiguous, flag it inline with [AMBIGUOUS — manual review required]
      rather than guessing intent.
