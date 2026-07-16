skills:
  - name: retrieve_documents
    description: Load all three CMC policy files and build a flat index of clauses keyed by document filename and clause number.
    input: >
      dir_path (str) to the directory containing policy_hr_leave.txt,
      policy_it_acceptable_use.txt, policy_finance_reimbursement.txt.
    output: >
      list of dicts, one per numbered clause across all three files, each
      with keys:
        filename (str, e.g. "policy_it_acceptable_use.txt"),
        section_num (str, e.g. "3"),
        section_title (str, e.g. "PERSONAL DEVICES (BYOD)"),
        clause_num (str, e.g. "3.1"),
        text (str, full clause text with continuation lines joined).
    error_handling: >
      Any of the three files missing → raise FileNotFoundError naming the
      missing filename. Empty file → clauses from other files still loaded,
      no crash. Malformed lines skipped silently (do not raise on the
      middle of a doc). Never invent a clause.

  - name: answer_question
    description: For one natural-language question, return either a single-source cited answer or the verbatim refusal template — never a blend.
    input: >
      question (str, free-form user text),
      clauses (list of dicts from retrieve_documents),
      confidence_threshold (int, default 2 = minimum matched non-stopword
      tokens for a clause to qualify),
      tie_margin (int, default 1 = if top clause's score exceeds second's by
      at most this many tokens AND they come from different documents,
      refuse instead of answering).
    output: >
      str containing either:
        (a) the clause text followed by newline then
            "(source: <filename> · section X.Y)", or
        (b) the exact refusal template string.
      No third form. No hedging phrases. No blending.
    error_handling: >
      Empty question → refusal template. Zero clauses indexed → raise
      RuntimeError (setup problem, not a user problem). Question containing
      only stopwords → refusal template. If any hedging phrase would appear
      in the output, the function must fall back to the refusal template.
