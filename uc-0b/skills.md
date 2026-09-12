skills:
   name: retrieve_policy
    description: Loads the HR leave policy .txt file and parses it into structured, numbered sections (e.g. 2.3, 2.4, 5.2) for downstream summarization.
    input:
      type: file path
      format: plain text file (.txt) containing decimal-numbered clauses (e.g. "2.3", "5.2")
    output:
      type: list of section objects
      format: "[{clause_id: str (e.g. '2.3'), text: str}, ...] one entry per numbered clause, in document order"
    error_handling: >
      If the file path does not exist, raise a clear error naming the
      missing path and stop — do not proceed on an assumed or empty
      document. If no decimal-numbered clauses are detected, raise a warning
      and fall back to treating the whole file as one section rather than
      silently returning nothing.

  - name: summarize_policy
    description: Produces a compliant, condensed summary of each retrieved clause, preserving every condition and every clause reference, and flags any clause it cannot safely summarize.
    input:
      type: list of section objects
      format: "[{clause_id: str, text: str}, ...] as produced by retrieve_policy"
    output:
      type: plain text
      format: "One labeled line per clause (e.g. '2.3: ...'), written to summary_hr_leave.txt, in the same order as the source"
    error_handling: >
      If a clause contains multiple conditions (e.g. two required approvers,
      an 'and'/'unless'/'provided that' construction), all conditions must
      be retained even if it takes more than one sentence — dropping any
      single condition is a failure. If a clause cannot be condensed without
      losing meaning, the skill must quote the clause verbatim in the
      output and prefix it with a '[VERBATIM — FLAGGED]' marker instead of
      producing a lossy paraphrase.
