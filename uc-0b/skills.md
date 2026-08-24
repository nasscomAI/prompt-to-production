# skills.md — UC-0B Policy Summarizer

skills:
  - name: retrieve_policy
    description: >
      Loads a plain-text policy document and returns its content structured as an
      ordered list of numbered sections and their sub-clauses, preserving all clause
      numbers, headings, and body text exactly as they appear in the source file.
    input: >
      file_path (str): absolute or relative path to a UTF-8 plain-text policy file.
    output: >
      A Python list of dicts, each with keys: section_number (str, e.g. "2.3"),
      section_heading (str, parent section heading), and text (str, full clause text).
      The list is ordered by appearance in the document.
    error_handling: >
      If the file is missing, raise FileNotFoundError with a clear message.
      If the file is empty, raise ValueError("Policy document is empty").
      Never return partial content silently — if fewer than 5 sections are detected,
      emit a warning to stderr before returning.

  - name: summarize_policy
    description: >
      Takes the structured section list produced by retrieve_policy and produces a
      complete, clause-faithful plain-text summary. Every clause in the input MUST
      appear in the output. Multi-condition obligations, numerical thresholds, and
      binding verbs are preserved verbatim. No external information is added.
    input: >
      sections (list of dicts): output of retrieve_policy.
      output_path (str): path where the summary .txt file will be written.
    output: >
      A UTF-8 plain-text file at output_path. Each summarised clause is preceded by
      its clause number in square brackets (e.g. [2.3]). A COMPLETENESS CHECK section
      at the bottom lists every clause number found in the source and confirms it is
      present in the summary.
    error_handling: >
      If any mandatory clause from the known critical list is absent from the source
      document, emit a MISSING CLAUSE warning to stderr. If a clause is too complex
      to paraphrase safely, output it verbatim with a [VERBATIM] annotation.
      Never crash — always write the output file even if warnings were emitted.

# ── Critical Clauses — All 10 Must Appear in Summary ─────────────────────────
# [2.3]  14-day advance notice required | binding verb: must
# [2.4]  Written approval required before leave commences. Verbal not valid. | must
# [2.5]  Unapproved absence = Loss of Pay regardless of subsequent approval | will
# [2.6]  Max 5 days carry-forward. Days above 5 forfeited on 31 December. | may / are forfeited
# [2.7]  Carry-forward days must be used January–March or forfeited | must
# [3.2]  3+ consecutive sick days requires medical cert within 48 hrs | requires
# [3.4]  Sick leave before/after holiday requires cert regardless of duration | requires
# [5.2]  LWP requires Department Head AND HR Director approval (BOTH required) | requires
# [5.3]  LWP >30 days requires Municipal Commissioner approval | requires
# [7.2]  Leave encashment during service not permitted under any circumstances | not permitted
